"""
SIPp Engine - Gerencia a execução dos processos do SIPp em threads de segundo plano.
Inclui validações de segurança, mascaramento de senhas em logs, streaming de saída e métricas em tempo real.
"""

import os
import subprocess
import threading
import time
from typing import Callable, Optional, Dict, Any

from core.paths import (
    BASE_DIR,
    get_project_path,
    resolve_scenario,
    resolve_pcap,
    get_subprocess_env,
    DEFAULT_SIPP_EXE
)
from core.sip_client import SipClient
from core.scenario_builder import ScenarioBuilder
from core.strategy_manager import StrategyManager
from core.sipp_downloader import SippLocator
from core.security import SecurityValidator


class SippEngine:
    """Motor de orquestração e monitoramento seguro do SIPp."""

    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.single_call_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.is_paused = False
        self.is_single_call_running = False
        
        self.stats_thread: Optional[threading.Thread] = None
        self.log_thread: Optional[threading.Thread] = None
        
        # Métricas em tempo real
        self.active_calls = 0
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.current_cps = 0.0

    def get_sipp_binary(self, configured_path: str = "") -> str:
        """Localiza o binário do SIPp ou retorna o configurado."""
        found = SippLocator.find_sipp(configured_path)
        return found if found else (configured_path if configured_path else DEFAULT_SIPP_EXE)

    # -------------------------------------------------------------------------
    # 1. TESTE DE REGISTRO SIP (com retorno para LED)
    # -------------------------------------------------------------------------
    def test_registration(
        self,
        config: Dict[str, Any],
        log_callback: Callable[[str, str], None],
        result_callback: Callable[[bool, str, Optional[float]], None]
    ):
        """
        Executa teste de registro SIP do ramal com autenticação Digest (RFC 3261 / RFC 2617).
        Utiliza o motor nativo SipClient em Python (independente de OpenSSL externo e com suporte a MD5 nativo).
        """
        def _worker():
            host = config.get("asterisk_ip", "").strip()
            port = config.get("asterisk_port", "5060")
            ramal = config.get("ramal", "").strip()
            auth_user = config.get("usuario_auth", "").strip() or ramal
            senha = config.get("senha", "")
            domain = config.get("sip_domain", host).strip() or host
            transport = config.get("transport", "u1")
            local_ip = config.get("local_ip", "").strip()

            # Validações de segurança
            val_host_ok, host_msg = SecurityValidator.validate_host(host)
            if not val_host_ok:
                log_callback(f"[REGISTRO] Erro de validação: {host_msg}", "ERROR")
                result_callback(False, host_msg, None)
                return

            val_port_ok, p_num = SecurityValidator.validate_port(port)
            if not val_port_ok:
                log_callback("[REGISTRO] Erro de validação: Porta SIP inválida (deve estar entre 1 e 65535).", "ERROR")
                result_callback(False, "Porta SIP inválida", None)
                return

            val_user_ok, user_msg = SecurityValidator.validate_sip_user(ramal, "Ramal")
            if not val_user_ok:
                log_callback(f"[REGISTRO] Erro de validação: {user_msg}", "ERROR")
                result_callback(False, user_msg, None)
                return

            target = f"{host}:{p_num}"
            log_callback(f"[REGISTRO] Enviando REGISTER para {target} ({transport.upper()}) | Ramal: {ramal} (Auth: {auth_user})...", "INFO")

            ok, code, msg, duration = SipClient.test_register(
                host=host,
                port=p_num,
                ramal=ramal,
                auth_user=auth_user,
                password=senha,
                domain=domain,
                transport=transport,
                timeout=6.0,
                local_ip=local_ip
            )

            if ok:
                log_callback(f"[REGISTRO] SUCESSO: Ramal {ramal} registrado com 200 OK em {duration}s.", "SUCCESS")
                result_callback(True, msg, duration)
            else:
                log_callback(f"[REGISTRO] ERRO (Código {code if code else 'Timeout'}): {msg}", "ERROR")
                result_callback(False, msg, None)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    # -------------------------------------------------------------------------
    # 2. CHAMADA ÚNICA (Ligar e Desligar teste rápido)
    # -------------------------------------------------------------------------
    def start_single_call(
        self,
        config: Dict[str, Any],
        destination: str,
        log_callback: Callable[[str, str], None],
        status_callback: Callable[[str], None]
    ):
        """Inicia 1 chamada de teste para o destino especificado."""
        if self.is_single_call_running:
            log_callback("[CHAMADA ÚNICA] Já existe uma chamada única em andamento.", "WARNING")
            return

        def _worker():
            self.is_single_call_running = True
            status_callback("Iniciando Chamada Única...")
            
            host = config.get("asterisk_ip", "").strip()
            port = config.get("asterisk_port", "5060")
            ramal = config.get("ramal", "").strip()
            auth_user = config.get("usuario_auth", "").strip() or ramal
            senha = config.get("senha", "")
            domain = config.get("sip_domain", host).strip() or host
            transport = config.get("transport", "u1")
            local_ip = config.get("local_ip", "").strip()

            val_dest_ok, dest_clean = SecurityValidator.validate_destination_number(destination)
            if not val_dest_ok:
                log_callback(f"[CHAMADA ÚNICA] Erro: {dest_clean}", "ERROR")
                self.is_single_call_running = False
                status_callback("Destino Inválido")
                return

            sipp_bin = self.get_sipp_binary(config.get("sipp_path", ""))
            target = f"{host}:{port}"

            pcap_file = config.get("pcap_file", "pcap/g711a.pcap").strip() or "pcap/g711a.pcap"

            # Gera XML com 30s de duração
            single_xml = get_project_path("single_call.xml")
            ScenarioBuilder.generate_single_call_xml("call.xml.template", single_xml, duracao_ms=30000, pcap_file=pcap_file)

            # Gera CSV (field0=auth_user, field1=senha, field2=dest_clean)
            csv_path = get_project_path("single_credenciais.csv")
            ScenarioBuilder.generate_credentials_csv([(auth_user, senha, dest_clean)], output_path=csv_path)

            cmd = [
                sipp_bin,
                target,
                "-sf", single_xml,
                "-inf", csv_path,
                "-t", transport,
                "-set", "domain", domain,
                "-set", "user", ramal,
                "-set", "dest", dest_clean,
                "-m", "1",
                "-r", "1",
                "-trace_err"
            ]
            if local_ip:
                cmd.extend(["-i", local_ip])

            local_port = config.get("local_port", "").strip()
            if local_port:
                val_lp_ok, lp_num = SecurityValidator.validate_port(local_port)
                if val_lp_ok:
                    cmd.extend(["-p", str(lp_num)])

            media_port = config.get("media_port", "").strip()
            if media_port:
                val_mp_ok, mp_num = SecurityValidator.validate_port(media_port)
                if val_mp_ok:
                    cmd.extend(["-mp", str(mp_num)])

            log_callback(f"[CHAMADA ÚNICA] Ligando para {dest_clean} via ramal {ramal}...", "INFO")
            
            try:
                self.single_call_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    cwd=BASE_DIR,
                    env=get_subprocess_env(),
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                status_callback(f"📞 Chamada Ativa ➔ {dest_clean}")

                # Monitora saída
                while self.single_call_process and self.single_call_process.poll() is None:
                    line = self.single_call_process.stdout.readline()
                    if line:
                        masked = SecurityValidator.mask_credentials(line.strip(), senha)
                        log_callback(f"[CHAMADA ÚNICA] {masked}", "DEBUG")
                    time.sleep(0.1)

                rc = self.single_call_process.returncode if self.single_call_process else 0
                if rc == 0:
                    log_callback(f"[CHAMADA ÚNICA] Chamada para {dest_clean} encerrada normalmente.", "SUCCESS")
                else:
                    log_callback(f"[CHAMADA ÚNICA] Chamada finalizada com código {rc}.", "WARNING")

            except Exception as e:
                log_callback(f"[CHAMADA ÚNICA] Erro: {e}", "ERROR")
            finally:
                self.is_single_call_running = False
                self.single_call_process = None
                status_callback("Chamada Finalizada")
                for f_tmp in [single_xml, csv_path]:
                    SecurityValidator.secure_delete_file(f_tmp)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def stop_single_call(self):
        """Desliga a chamada única em andamento."""
        if self.single_call_process and self.single_call_process.poll() is None:
            try:
                self.single_call_process.terminate()
                time.sleep(0.3)
                if self.single_call_process.poll() is None:
                    self.single_call_process.kill()
            except Exception:
                pass
        self.is_single_call_running = False

    # -------------------------------------------------------------------------
    # 3. TESTE DE CARGA (SIMULTÂNEAS / ESTRATÉGIA)
    # -------------------------------------------------------------------------
    def start_load_test(
        self,
        config: Dict[str, Any],
        log_callback: Callable[[str, str], None],
        stats_callback: Callable[[Dict[str, Any]], None],
        finished_callback: Callable[[int], None]
    ) -> bool:
        """Inicia o teste de carga completo com SIPp."""
        if self.is_running:
            log_callback("[TESTE] Teste de carga já está em execução.", "WARNING")
            return False

        # Valida destinos
        destinations = config.get("destinations", [])
        valid, msg = StrategyManager.validate_destinations(destinations)
        if not valid:
            log_callback(f"[TESTE] ERRO de validação: {msg}", "ERROR")
            return False

        # Prepara cenários e CSV
        dur_min = int(config.get("duracao_min_ms", 10000))
        dur_max = int(config.get("duracao_max_ms", 60000))
        dur_fixa = bool(config.get("duracao_fixa", False))
        pcap_file = config.get("pcap_file", "pcap/g711a.pcap").strip() or "pcap/g711a.pcap"

        call_xml_path = get_project_path("call.xml")
        ok, err = ScenarioBuilder.generate_call_xml(
            template_path="call.xml.template",
            output_path=call_xml_path,
            duracao_min_ms=dur_min,
            duracao_max_ms=dur_max,
            duracao_fixa=dur_fixa,
            pcap_file=pcap_file
        )
        if not ok:
            log_callback(f"[TESTE] ERRO ao gerar call.xml: {err}", "ERROR")
            return False

        # Gera pool de credenciais/destinos ponderados (field0=auth_user, field1=senha, field2=dest)
        ramal = config.get("ramal", "").strip()
        auth_user = config.get("usuario_auth", "").strip() or ramal
        senha = config.get("senha", "")
        pool = StrategyManager.generate_weighted_destination_pool(
            destinations=destinations,
            ramal=auth_user,
            senha=senha,
            pool_size=1000,
            token_prefix=config.get("human_token_prefix", "AGENT_")
        )
        
        # Modo SEQUENTIAL ou RANDOM
        csv_mode = "RANDOM" if config.get("dial_mode") == "human_random" else "SEQUENTIAL"
        cred_csv_path = get_project_path("credenciais.csv")
        ScenarioBuilder.generate_credentials_csv(pool, output_path=cred_csv_path, mode=csv_mode)

        # Monta comando SIPp
        sipp_bin = self.get_sipp_binary(config.get("sipp_path", ""))
        host = config.get("asterisk_ip", "").strip()
        port = config.get("asterisk_port", "5060")
        target = f"{host}:{port}"
        domain = config.get("sip_domain", host).strip() or host
        transport = config.get("transport", "u1")
        local_ip = config.get("local_ip", "").strip()
        simultaneas = int(config.get("simultaneas", 100))
        total = int(config.get("total", 0))
        rate = int(config.get("rate", 50))
        rate_period = int(config.get("rate_period", 1000))

        # Pega primeiro destino do pool para a variável [$dest]
        primeiro_dest = pool[0][2] if pool else "22221864"

        cmd = [
            sipp_bin,
            target,
            "-sf", call_xml_path,
            "-inf", cred_csv_path,
            "-t", transport,
            "-set", "domain", domain,
            "-set", "user", ramal,
            "-set", "dest", primeiro_dest,
            "-l", str(simultaneas),
            "-r", str(rate),
            "-rp", str(rate_period),
            "-trace_err",
            "-trace_stat",
            "-stf", get_project_path("stats.csv"),
            "-fd", "1s"
        ]

        if total > 0:
            cmd.extend(["-m", str(total)])

        if local_ip:
            cmd.extend(["-i", local_ip])

        local_port = config.get("local_port", "").strip()
        if local_port:
            val_lp_ok, lp_num = SecurityValidator.validate_port(local_port)
            if val_lp_ok:
                cmd.extend(["-p", str(lp_num)])

        media_port = config.get("media_port", "").strip()
        if media_port:
            val_mp_ok, mp_num = SecurityValidator.validate_port(media_port)
            if val_mp_ok:
                cmd.extend(["-mp", str(mp_num)])

        log_callback("==================================================", "HEADER")
        log_callback("🚀 INICIANDO TESTE DE CARGA SIPP", "HEADER")
        log_callback(f"  Alvo: {target} ({transport}) | Domínio: {domain}", "INFO")
        log_callback(f"  Ramal: {ramal} (Auth: {auth_user}) | Teto Simultâneas: {simultaneas} | Total: {'Ilimitado' if total == 0 else total}", "INFO")
        log_callback(f"  Taxa: {rate} chamadas / {rate_period}ms | Duração: {dur_min}-{dur_max}ms", "INFO")
        log_callback(f"  Destinos Ativos ({len(config.get('destinations', []))} configurados):", "INFO")
        for d in config.get("destinations", []):
            if d.get("enabled") and d.get("number"):
                log_callback(f"    - {d.get('number')} ({d.get('description', 'Sem desc')}) [Peso: {d.get('weight')}]", "INFO")
        log_callback("==================================================", "HEADER")

        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=BASE_DIR,
                env=get_subprocess_env(),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.is_running = True
            self.is_paused = False

            # Thread para ler stdout
            def _read_stdout():
                while self.process and self.process.poll() is None:
                    line = self.process.stdout.readline()
                    if line:
                        clean = line.strip()
                        if clean:
                            masked = SecurityValidator.mask_credentials(clean, senha)
                            log_callback(masked, "STDOUT")
                    time.sleep(0.05)

            self.log_thread = threading.Thread(target=_read_stdout, daemon=True)
            self.log_thread.start()

            # Thread para monitorar estatísticas do stats.csv
            def _monitor_stats():
                stats_file = get_project_path("stats.csv")
                while self.is_running and self.process and self.process.poll() is None:
                    stats = self._parse_stats_csv(stats_file, simultaneas)
                    if stats:
                        stats_callback(stats)
                    time.sleep(1.0)

                rc = self.process.returncode if self.process else 0
                self.is_running = False
                log_callback(f"🛑 Teste de carga finalizado (Código de saída: {rc}).", "SUCCESS" if rc == 0 else "WARNING")
                finished_callback(rc)
                SecurityValidator.secure_delete_file(cred_csv_path)

            self.stats_thread = threading.Thread(target=_monitor_stats, daemon=True)
            self.stats_thread.start()

            return True
        except Exception as e:
            self.is_running = False
            log_callback(f"[TESTE] ERRO ao iniciar SIPp: {e}", "ERROR")
            SecurityValidator.secure_delete_file(cred_csv_path)
            return False

    def _parse_stats_csv(self, file_path: str, max_simultaneas: int) -> Optional[Dict[str, Any]]:
        """Lê o arquivo stats.csv gerado pelo SIPp para extrair métricas."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = [line.strip() for line in f if line.strip()]
                if len(lines) < 2:
                    return None

                header = [h.strip() for h in lines[0].split(";")]
                last_row = [v.strip() for v in lines[-1].split(";")]

                stats = {
                    "active_calls": 0,
                    "max_simultaneas": max_simultaneas,
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "cps": 0.0
                }

                for i, col in enumerate(header):
                    if i < len(last_row):
                        val_str = last_row[i]
                        col_lower = col.lower()
                        
                        try:
                            if "currentcall" in col_lower or "active" in col_lower:
                                stats["active_calls"] = int(val_str)
                            elif "totalcallcreated" in col_lower or "totalcall" in col_lower:
                                stats["total_calls"] = int(val_str)
                            elif "successfulcall" in col_lower or "successful" in col_lower:
                                stats["successful_calls"] = int(val_str)
                            elif "failedcall" in col_lower or "failed" in col_lower:
                                stats["failed_calls"] = int(val_str)
                            elif "callrate" in col_lower or "cps" in col_lower:
                                stats["cps"] = float(val_str.replace(",", "."))
                        except ValueError:
                            pass

                return stats
        except Exception:
            return None

    # -------------------------------------------------------------------------
    # 4. CONTROLES EM TEMPO REAL (Pausar, Parar Suave, Kill)
    # -------------------------------------------------------------------------
    def send_key(self, key: str) -> bool:
        """Envia um comando de tecla para o processo SIPp via stdin."""
        if self.process and self.process.poll() is None and self.process.stdin:
            try:
                self.process.stdin.write(key)
                self.process.stdin.flush()
                return True
            except Exception:
                return False
        return False

    def soft_stop(self) -> bool:
        """Envia tecla 'q' para saída suave (aguarda chamadas ativas terminarem)."""
        return self.send_key("q")

    def pause_resume(self) -> bool:
        """Envia tecla 'p' para pausar ou retomar criação de chamadas."""
        ok = self.send_key("p")
        if ok:
            self.is_paused = not self.is_paused
        return ok

    def kill_all(self):
        """Derruba todas as chamadas imediatamente e força o encerramento do SIPp."""
        self.is_running = False
        self.is_single_call_running = False

        if self.process:
            try:
                self.process.terminate()
                time.sleep(0.2)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception:
                pass
            self.process = None

        if self.single_call_process:
            try:
                self.single_call_process.kill()
            except Exception:
                pass
            self.single_call_process = None

        # No Windows, garante que nenhum sipp.exe ficou órfão
        if os.name == 'nt':
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", "sipp.exe", "/T"],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception:
                pass

        # Limpa temporários
        for f in ["credenciais.csv", "single_credenciais.csv", "credenciais_reg.csv"]:
            SecurityValidator.secure_delete_file(get_project_path(f))
