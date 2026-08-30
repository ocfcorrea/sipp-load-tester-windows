"""
Config Manager - Gerencia o salvamento e carregamento de configurações do aplicativo.
Persiste parâmetros SIP, estratégias de discagem e lista de destinos ponderados em JSON.
"""

import json
import os
from typing import Dict, Any, List

CONFIG_FILE = "config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    # Conexão SIP (Aba 1)
    "asterisk_ip": "192.168.68.205",
    "asterisk_port": "5060",
    "transport": "u1",  # u1 = UDP, t1 = TCP
    "sip_domain": "192.168.68.205",
    "ramal": "108$1002",
    "usuario_auth": "108$1002",
    "senha": "<*L5-Callbox*>",
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
    """Carrega e persiste as configurações em arquivo JSON local."""

    def __init__(self, file_path: str = CONFIG_FILE):
        self.file_path = file_path
        self.config: Dict[str, Any] = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Lê o arquivo config.json ou cria com valores padrão se não existir."""
        if not os.path.exists(self.file_path):
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            
            # Mescla com defaults para garantir chaves novas
            merged = DEFAULT_CONFIG.copy()
            merged.update(saved)
            
            # Garante que lista de destinos tem tamanho 10
            dests = merged.get("destinations", [])
            while len(dests) < 10:
                dests.append({"enabled": False, "number": "", "description": "", "weight": 10})
            merged["destinations"] = dests[:10]
            
            return merged
        except Exception as e:
            print(f"[ConfigManager] Erro ao ler {self.file_path}: {e}. Usando padrões.")
            return DEFAULT_CONFIG.copy()

    def save_config(self, new_config: Dict[str, Any] = None) -> bool:
        """Salva o dicionário de configurações no arquivo JSON."""
        if new_config is not None:
            self.config = new_config

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ConfigManager] Erro ao salvar {self.file_path}: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value

    def get_active_destinations(self) -> List[Dict[str, Any]]:
        """Retorna apenas os destinos habilitados e com número preenchido."""
        return [
            d for d in self.config.get("destinations", [])
            if d.get("enabled", False) and str(d.get("number", "")).strip()
        ]
