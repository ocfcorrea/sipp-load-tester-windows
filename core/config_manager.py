"""
Config Manager - Gerencia o salvamento e carregamento de configurações do aplicativo.
Persiste parâmetros SIP e estratégias de discagem em JSON, com suporte a variáveis de ambiente (.env)
para proteção estrita de credenciais sensíveis (Zero Leaks).
"""

import json
import os
from typing import Dict, Any, List

try:
    from dotenv import load_dotenv, set_key
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

CONFIG_FILE = "config.json"
ENV_FILE = ".env"

DEFAULT_CONFIG: Dict[str, Any] = {
    # Conexão SIP (Aba 1)
    "asterisk_ip": "192.168.68.205",
    "asterisk_port": "5060",
    "transport": "u1",  # u1 = UDP, t1 = TCP
    "sip_domain": "192.168.68.205",
    "ramal": "108$1002",
    "usuario_auth": "108$1002",
    "senha": "",  # Protegido no .env por padrão
    "local_ip": "",
    "local_port": "",  # Vazio = porta aleatória / dinâmica
    "media_port": "6000",  # Porta base RTP
    "pcap_file": "pcap/g711a.pcap",
    "sipp_path": "bin/sipp/sipp.exe",
    
    # Parâmetros de Chamada & Carga (Aba 2)
    "simultaneas": 100,
    "total": 0,  # 0 = Ilimitado / contínuo
    "rate": 50,
    "rate_period": 1000,
    "duracao_min_ms": 10000,
    "duracao_max_ms": 60000,
    "duracao_fixa": False,
    "pcap_ms": 7000,
    
    # Modo de Discagem
    "dial_mode": "rate",  # "rate" ou "human_random"
    "human_min_interval_ms": 200,
    "human_max_interval_ms": 1500,
    "human_burst_chance": 15,
    "human_token_prefix": "L5_AGENT_",
    
    # Destino para Chamada Única Rápida
    "single_call_dest": "22221864",
    
    # Destinos Ponderados (1 a 10)
    "destinations": [
        {"enabled": True, "number": "22221864", "description": "URA Principal", "weight": 50},
        {"enabled": True, "number": "9999", "description": "Echo Test", "weight": 30},
        {"enabled": True, "number": "1001", "description": "Fila Atendimento", "weight": 20},
        {"enabled": False, "number": "", "description": "", "weight": 10},
        {"enabled": False, "number": "", "description": "", "weight": 10},
        {"enabled": False, "number": "", "description": "", "weight": 10},
        {"enabled": False, "number": "", "description": "", "weight": 10},
        {"enabled": False, "number": "", "description": "", "weight": 10},
        {"enabled": False, "number": "", "description": "", "weight": 10},
        {"enabled": False, "number": "", "description": "", "weight": 10},
    ]
}


class ConfigManager:
    """Carrega e persiste as configurações protegendo credenciais com .env."""

    def __init__(self, file_path: str = CONFIG_FILE, env_path: str = ENV_FILE):
        self.file_path = file_path
        self.env_path = env_path
        self._load_env_file()
        self.config: Dict[str, Any] = self.load_config()

    def _load_env_file(self):
        """Carrega variáveis do arquivo .env com dotenv ou parser nativo."""
        if os.path.exists(self.env_path):
            if DOTENV_AVAILABLE:
                load_dotenv(self.env_path, override=True)
            else:
                try:
                    with open(self.env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            clean = line.strip()
                            if clean and not clean.startswith("#") and "=" in clean:
                                k, v = clean.split("=", 1)
                                os.environ[k.strip()] = v.strip()
                except Exception:
                    pass

    def load_config(self) -> Dict[str, Any]:
        """Lê config.json e mescla com variáveis de ambiente do .env."""
        base_cfg = DEFAULT_CONFIG.copy()

        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                base_cfg.update(saved)
            except Exception as e:
                print(f"[ConfigManager] Erro ao ler {self.file_path}: {e}. Usando padrões.")

        # Injeta variáveis de ambiente (.env) com prioridade para segredos
        if os.getenv("SIP_SENHA"):
            base_cfg["senha"] = os.getenv("SIP_SENHA")
        if os.getenv("SIP_RAMAL"):
            base_cfg["ramal"] = os.getenv("SIP_RAMAL")
        if os.getenv("SIP_USUARIO_AUTH"):
            base_cfg["usuario_auth"] = os.getenv("SIP_USUARIO_AUTH")
        if os.getenv("SIP_ASTERISK_IP"):
            base_cfg["asterisk_ip"] = os.getenv("SIP_ASTERISK_IP")
        if os.getenv("SIP_ASTERISK_PORT"):
            base_cfg["asterisk_port"] = os.getenv("SIP_ASTERISK_PORT")
        if os.getenv("SIP_DOMAIN"):
            base_cfg["sip_domain"] = os.getenv("SIP_DOMAIN")

        # Garante lista de destinos com 10 slots
        dests = base_cfg.get("destinations", [])
        while len(dests) < 10:
            dests.append({"enabled": False, "number": "", "description": "", "weight": 10})
        base_cfg["destinations"] = dests[:10]

        return base_cfg

    def save_config(self, new_config: Dict[str, Any] = None) -> bool:
        """
        Salva parâmetros gerais no config.json (com senha vazia para segurança)
        e salva credenciais confidenciais no .env (ignorado no git).
        """
        if new_config is not None:
            self.config = new_config

        try:
            # 1. Salva credenciais confidenciais no .env
            self._save_env_file()

            # 2. Salva config.json higienizado (sem vazar senha)
            safe_json_config = self.config.copy()
            safe_json_config["senha"] = ""  # Sempre limpo no JSON para evitar vazamentos em git commit

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(safe_json_config, f, indent=4, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"[ConfigManager] Erro ao salvar {self.file_path}: {e}")
            return False

    def _save_env_file(self):
        """Atualiza o arquivo .env de forma segura."""
        env_content = (
            "# ============================================================\n"
            "# SIPp Load Tester Pro - Credenciais e Variáveis de Ambiente\n"
            "# ESTE ARQUIVO É SEGURO E NUNCA DEVE SER COMITADO NO GIT (.gitignore)\n"
            "# ============================================================\n\n"
            f"SIP_ASTERISK_IP={self.config.get('asterisk_ip', '')}\n"
            f"SIP_ASTERISK_PORT={self.config.get('asterisk_port', '5060')}\n"
            f"SIP_DOMAIN={self.config.get('sip_domain', '')}\n"
            f"SIP_RAMAL={self.config.get('ramal', '')}\n"
            f"SIP_USUARIO_AUTH={self.config.get('usuario_auth', '')}\n"
            f"SIP_SENHA={self.config.get('senha', '')}\n"
        )
        try:
            with open(self.env_path, "w", encoding="utf-8") as f:
                f.write(env_content)
        except Exception as e:
            print(f"[ConfigManager] Erro ao salvar {self.env_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value

    def get_active_destinations(self) -> List[Dict[str, Any]]:
        """Retorna apenas os destinos habilitados e com número preenchido."""
        return [
            d for d in self.config.get("destinations", [])
            if d.get("enabled") and d.get("number", "").strip()
        ]
