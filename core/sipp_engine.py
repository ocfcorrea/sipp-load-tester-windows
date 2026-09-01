"""
SIPp Engine - Motor de Geração de Carga e Simultaneidade SIP com Autenticação Digest MD5 Nativa.
Suporta alta performance multithread, controle estrito de simultaneidade (-l), taxa de disparo (-r, -rp),
pesos ponderados de destino, simulação randômica humana e métricas em tempo real sem dependência de OpenSSL externo.
"""

import os
import subprocess
import threading
import time
import random
from typing import Callable, Optional, Dict, Any

from core.paths import get_project_path
from core.sip_client import SipClient
from core.strategy_manager import StrategyManager
from core.sipp_downloader import SippLocator
from core.security import SecurityValidator


class SippEngine:
    """Motor de orquestração e geração de carga SIP de alta performance."""

    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.is_single_call_running = False

        self.load_stop_event = threading.Event()
        self.single_call_stop_event = threading.Event()

        self.stats_thread: Optional[threading.Thread] = None
        self.dispatcher_thread: Optional[threading.Thread] = None

        # Lock para controle seguro de concorrência
        self.lock = threading.Lock()

        # Métricas em tempo real
        self.active_calls = 0
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.current_cps = 0.0

        # Processos legados (para compatibilidade)
        self.process: Optional[subprocess.Popen] = None
        self.single_call_process: Optional[subprocess.Popen] = None
        self.background_pid: Optional[int] = None

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
        Utiliza o motor nativo SipClient em Python (suporte nativo a MD5).
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
        """Inicia 1 chamada de teste para o destino especificado usando SipClient nativo com Digest MD5."""
        if self.is_single_call_running:
            log_callback("[CHAMADA ÚNICA] Já existe uma chamada única em andamento.", "WARNING")
            return

        def _worker():
            self.is_single_call_running = True
            self.single_call_stop_event.clear()
            status_callback("Iniciando Chamada Única...")

            host = config.get("asterisk_ip", "").strip()
            port = int(config.get("asterisk_port", 5060) or 5060)
            ramal = config.get("ramal", "").strip()
            auth_user = config.get("usuario_auth", "").strip() or ramal
            senha = config.get("senha", "")
            domain = config.get("sip_domain", host).strip() or host
            transport = config.get("transport", "u1")
            local_ip = config.get("local_ip", "").strip()
            media_port = int(config.get("media_port", 6000) or 6000)
            pcap_file = config.get("pcap_file", "pcap/g711a.pcap").strip() or "pcap/g711a.pcap"

            val_dest_ok, dest_clean = SecurityValidator.validate_destination_number(destination)
            if not val_dest_ok:
                log_callback(f"[CHAMADA ÚNICA] Erro no destino: {dest_clean}", "ERROR")
                self.is_single_call_running = False
                status_callback("Destino Inválido")
                return

            log_callback(f"[CHAMADA ÚNICA] Ligando para {dest_clean} via ramal {ramal} no PBX {host}:{port}...", "INFO")

            try:
                ok, code, msg = SipClient.single_call(
                    host=host,
                    port=port,
                    ramal=ramal,
                    auth_user=auth_user,
                    password=senha,
                    destination=dest_clean,
                    domain=domain,
                    transport=transport,
                    duration_sec=30.0,
                    local_ip=local_ip,
                    media_port=media_port,
                    pcap_file=pcap_file,
                    log_callback=log_callback,
                    status_callback=status_callback,
                    stop_event=self.single_call_stop_event
                )
                if ok:
                    log_callback(f"[CHAMADA ÚNICA] {msg}", "SUCCESS")
                else:
                    log_callback(f"[CHAMADA ÚNICA] Falha na chamada: {msg}", "ERROR")
            except Exception as e:
                log_callback(f"[CHAMADA ÚNICA] Erro inesperado: {e}", "ERROR")
            finally:
                self.is_single_call_running = False
                status_callback("Pronto")

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def stop_single_call(self):
        """Desliga a chamada única em andamento."""
        self.single_call_stop_event.set()
        self.is_single_call_running = False

    # -------------------------------------------------------------------------
    # 3. TESTE DE CARGA (SIMULTÂNEAS / ESTRATÉGIA) - MOTOR NATIVO MD5
    # -------------------------------------------------------------------------
    def start_load_test(
        self,
        config: Dict[str, Any],
        log_callback: Callable[[str, str], None],
        stats_callback: Callable[[Dict[str, Any]], None],
        finished_callback: Optional[Callable[[int], None]] = None
    ) -> bool:
        """Inicia o teste de carga completo multithread nativo com Digest MD5."""
        if self.is_running:
            log_callback("[TESTE] Teste de carga já está em execução.", "WARNING")
            return False

        # Valida destinos
        destinations = config.get("destinations", [])
        valid, msg = StrategyManager.validate_destinations(destinations)
        if not valid:
            log_callback(f"[TESTE] ERRO de validação: {msg}", "ERROR")
            return False

        host = config.get("asterisk_ip", "").strip()
        port = int(config.get("asterisk_port", 5060) or 5060)
        ramal = config.get("ramal", "").strip()
        auth_user = config.get("usuario_auth", "").strip() or ramal
        senha = config.get("senha", "")
        domain = config.get("sip_domain", host).strip() or host
        transport = config.get("transport", "u1")
        pcap_file = config.get("pcap_file", "pcap/g711a.pcap").strip() or "pcap/g711a.pcap"

        # Auto-detecção de IPv4 local
        local_ip = config.get("local_ip", "").strip()
        if not local_ip:
            try:
                import socket
                s_probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s_probe.connect((host, port if port > 0 else 5060))
                local_ip = s_probe.getsockname()[0]
                s_probe.close()
            except Exception:
                local_ip = "127.0.0.1"

        simultaneas = int(config.get("simultaneas", 100))
        total_limit = int(config.get("total", 0))
        dur_min_ms = int(config.get("duracao_min_ms", 10000))
        dur_max_ms = int(config.get("duracao_max_ms", 60000))
        dur_fixa = bool(config.get("duracao_fixa", False))
        dial_mode = config.get("dial_mode", "rate")

        rate = int(config.get("rate", 50))
        rate_period_ms = int(config.get("rate_period", 1000))

        # Gera pool ponderado de destinos
        pool = StrategyManager.generate_weighted_destination_pool(
            destinations=destinations,
            ramal=auth_user,
            senha=senha,
            pool_size=1000,
            token_prefix=config.get("human_token_prefix", "AGENT_")
        )

        log_callback("==================================================", "HEADER")
        log_callback("🚀 INICIANDO TESTE DE CARGA (MOTOR SIP PRO MD5)", "HEADER")
        log_callback(f"  Alvo PBX: {host}:{port} ({transport.upper()}) | Domínio: {domain}", "INFO")
        log_callback(f"  IP Local de Envio: {local_ip} | Ramal: {ramal} (Auth: {auth_user})", "INFO")
        log_callback(f"  Teto de Simultâneas (-l): {simultaneas} | Total: {'Ilimitado' if total_limit == 0 else total_limit}", "INFO")
        log_callback(f"  Modo: {'Simulação Humana Orgânica' if dial_mode == 'human_random' else f'Taxa Constante ({rate} ch/{rate_period_ms}ms)'}", "INFO")
        log_callback(f"  Duração da Chamada: {dur_min_ms}ms{' (Fixa)' if dur_fixa else f' a {dur_max_ms}ms'}", "INFO")
        log_callback(f"  Áudio RTP PCAP: {pcap_file}", "INFO")
        log_callback(f"  Destinos Ativos ({len(destinations)} configurados):", "INFO")
        for d in destinations:
            if d.get("enabled") and d.get("number"):
                log_callback(f"    - Destino: {d.get('number')} ({d.get('description', 'Sem desc')}) [Peso: {d.get('weight')}]", "INFO")
        log_callback("==================================================", "HEADER")

        # Reseta métricas
        with self.lock:
            self.active_calls = 0
            self.total_calls = 0
            self.successful_calls = 0
            self.failed_calls = 0
            self.current_cps = 0.0

        self.is_running = True
        self.is_paused = False
        self.load_stop_event.clear()

        # Thread de cada chamada individual
        def _call_worker(call_num: int, dest_number: str, duration_sec: float, media_port: int):
            with self.lock:
                self.active_calls += 1

            try:
                ok, code, msg = SipClient.single_call(
                    host=host,
                    port=port,
                    ramal=ramal,
                    auth_user=auth_user,
                    password=senha,
                    destination=dest_number,
                    domain=domain,
                    transport=transport,
                    duration_sec=duration_sec,
                    local_ip=local_ip,
                    media_port=media_port,
                    pcap_file=pcap_file,
                    stop_event=self.load_stop_event
                )
                with self.lock:
                    if ok:
                        self.successful_calls += 1
                    else:
                        self.failed_calls += 1

                if ok:
                    log_callback(f"🎉 [PBX] Chamada #{call_num} ➔ {dest_number} atendida (200 OK)! Mantida por {duration_sec:.1f}s", "SUCCESS")
                else:
                    log_callback(f"⚠️ [PBX] Chamada #{call_num} ➔ {dest_number} falhou (SIP {code}: {msg})", "WARNING")

            except Exception as e:
                with self.lock:
                    self.failed_calls += 1
                log_callback(f"❌ [CHAMADA #{call_num}] Erro: {e}", "ERROR")
            finally:
                with self.lock:
                    self.active_calls -= 1

        # Thread despachante (mantém a simultaneidade constante)
        def _dispatcher_loop():
            call_counter = 0
            base_media_port = int(config.get("media_port", 6000) or 6000)

            while self.is_running and not self.load_stop_event.is_set():
                if self.is_paused:
                    time.sleep(0.2)
                    continue

                with self.lock:
                    current_active = self.active_calls
                    current_total = self.total_calls

                # Verifica se atingiu limite total
                if total_limit > 0 and current_total >= total_limit:
                    if current_active == 0:
                        break
                    time.sleep(0.2)
                    continue

                # Se há vaga para novas chamadas até o teto de simultâneas
                if current_active < simultaneas:
                    call_counter += 1
                    with self.lock:
                        self.total_calls += 1

                    # Seleciona destino ponderado
                    selected_item = random.choice(pool) if pool else (auth_user, senha, "1500")
                    dest_num = selected_item[2]

                    # Calcula duração sorteada em segundos
                    if dur_fixa or dur_min_ms >= dur_max_ms:
                        dur_sec = max(1.0, dur_min_ms / 1000.0)
                    else:
                        dur_sec = random.uniform(dur_min_ms / 1000.0, dur_max_ms / 1000.0)

                    media_p = base_media_port + ((call_counter % 2000) * 2)

                    log_callback(f"➔ [DISPARO] Chamada #{call_counter} para {dest_num} (Alvo: {simultaneas} simultâneas)", "INFO")

                    t = threading.Thread(
                        target=_call_worker,
                        args=(call_counter, dest_num, dur_sec, media_p),
                        daemon=True
                    )
                    t.start()

                    # Controle de cadência
                    if dial_mode == "human_random":
                        h_min = int(config.get("human_min_interval_ms", 200))
                        h_max = int(config.get("human_max_interval_ms", 1500))
                        h_burst = int(config.get("human_burst_chance", 15))
                        interval_ms = StrategyManager.get_random_human_interval(h_min, h_max, h_burst)
                        time.sleep(max(0.01, interval_ms / 1000.0))
                    else:
                        interval_sec = (rate_period_ms / 1000.0) / max(1, rate)
                        time.sleep(max(0.01, interval_sec))
                else:
                    time.sleep(0.05)

            self.is_running = False

            log_callback("🛑 Teste de carga finalizado.", "INFO")
            if finished_callback:
                finished_callback(0)

        # Thread de monitoramento de métricas
        def _metrics_reporter():
            last_total = 0
            last_time = time.time()
            last_heartbeat = time.time()

            while self.is_running:
                time.sleep(0.5)
                now = time.time()
                dt = now - last_time

                with self.lock:
                    cur_active = self.active_calls
                    cur_total = self.total_calls
                    cur_succ = self.successful_calls
                    cur_fail = self.failed_calls

                cps = round((cur_total - last_total) / dt, 1) if dt > 0 else 0.0
                last_total = cur_total
                last_time = now

                stats = {
                    "active_calls": cur_active,
                    "max_simultaneas": simultaneas,
                    "total_calls": cur_total,
                    "successful_calls": cur_succ,
                    "failed_calls": cur_fail,
                    "cps": max(0.0, cps)
                }
                stats_callback(stats)

                # Batimento periódico a cada 3 segundos
                if now - last_heartbeat >= 3.0:
                    last_heartbeat = now
                    log_callback(
                        f"📊 [PAINEL] Simultâneas: {cur_active}/{simultaneas} | "
                        f"Disparadas: {cur_total} | "
                        f"Atendidas (200 OK): {cur_succ} | "
                        f"Falhas: {cur_fail} | "
                        f"Taxa: {cps:.1f} cps",
                        "INFO"
                    )

        self.dispatcher_thread = threading.Thread(target=_dispatcher_loop, daemon=True)
        self.dispatcher_thread.start()

        self.stats_thread = threading.Thread(target=_metrics_reporter, daemon=True)
        self.stats_thread.start()

        return True

    # -------------------------------------------------------------------------
    # 4. CONTROLES EM TEMPO REAL (Pausar, Parar Suave, Kill)
    # -------------------------------------------------------------------------
    def pause_resume(self) -> bool:
        """Pausa ou retoma a criação de novas chamadas mantendo as ativas."""
        if not self.is_running:
            return False
        self.is_paused = not self.is_paused
        return True

    def soft_stop(self) -> bool:
        """Saída suave: interrompe criação de novas chamadas e aguarda as ativas encerrarem."""
        if not self.is_running:
            return False
        self.is_running = False
        return True

    def kill_all(self):
        """Derruba todas as chamadas imediatamente."""
        self.is_running = False
        self.is_single_call_running = False
        self.load_stop_event.set()
        self.single_call_stop_event.set()

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
        import glob
        for f in glob.glob(os.path.join(BASE_DIR, "call_*_shortmessages.log")) + \
                 glob.glob(os.path.join(BASE_DIR, "call_*_errors.log")) + \
                 ["credenciais.csv", "single_credenciais.csv", "credenciais_reg.csv", "stats.csv"]:
            target_path = f if os.path.isabs(f) else get_project_path(f)
            SecurityValidator.secure_delete_file(target_path)
