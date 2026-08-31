"""
Paths Manager - Gerenciador centralizado de diretórios e caminhos de recursos.
Garante que todos os módulos acessem arquivos com caminhos absolutos baseados na raiz do projeto,
evitando erros de diretório de trabalho relativo (Current Working Directory) entre diferentes máquinas.
"""

import os
import sys
import shutil
from typing import Optional

# Diretório raiz do projeto (onde app.py reside)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Diretórios principais
CORE_DIR = os.path.join(BASE_DIR, "core")
GUI_DIR = os.path.join(BASE_DIR, "gui")
BIN_DIR = os.path.join(BASE_DIR, "bin")
SIPP_DIR = os.path.join(BIN_DIR, "sipp")
SCENARIOS_DIR = os.path.join(BASE_DIR, "scenarios")
PCAP_DIR = os.path.join(BASE_DIR, "pcap")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
TESTS_DIR = os.path.join(BASE_DIR, "tests")

# Arquivos de configuração e dados
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")
ENV_EXAMPLE_FILE = os.path.join(BASE_DIR, ".env.example")

# Executável SIPp padrão para Windows
DEFAULT_SIPP_EXE = os.path.join(SIPP_DIR, "sipp.exe" if sys.platform == "win32" else "sipp")
DEFAULT_PCAP_FILE = os.path.join(PCAP_DIR, "g711a.pcap")


def get_project_path(*subpaths: str) -> str:
    """Retorna o caminho absoluto de um arquivo ou diretório a partir da raiz do projeto."""
    return os.path.normpath(os.path.join(BASE_DIR, *subpaths))


def resolve_scenario(filename: str) -> str:
    """
    Resolve o caminho absoluto de um arquivo de cenário XML ou template.
    Busca primeiro em scenarios/, depois na raiz do projeto.
    """
    in_scenarios = os.path.join(SCENARIOS_DIR, filename)
    if os.path.exists(in_scenarios):
        return in_scenarios
    
    in_root = os.path.join(BASE_DIR, filename)
    if os.path.exists(in_root):
        return in_root
        
    return in_scenarios


def resolve_pcap(filename: str = "g711a.pcap") -> str:
    """Resolve o caminho absoluto de um arquivo PCAP."""
    if not filename:
        return DEFAULT_PCAP_FILE
        
    if os.path.isabs(filename) and os.path.exists(filename):
        return filename
        
    in_pcap = os.path.join(PCAP_DIR, os.path.basename(filename))
    if os.path.exists(in_pcap):
        return in_pcap
        
    in_root = os.path.join(BASE_DIR, filename)
    if os.path.exists(in_root):
        return in_root
        
    return os.path.join(PCAP_DIR, filename)


def ensure_env_file() -> bool:
    """
    Garante a existência do arquivo .env.
    Se o .env não existir (ex: clone recente do git), copia de .env.example
    ou cria um arquivo inicial seguro.
    """
    if os.path.exists(ENV_FILE):
        return True

    try:
        if os.path.exists(ENV_EXAMPLE_FILE):
            shutil.copy2(ENV_EXAMPLE_FILE, ENV_FILE)
            return True
        else:
            initial_content = (
                "# ============================================================\n"
                "# SIPp Load Tester Pro - Variáveis de Ambiente\n"
                "# ============================================================\n\n"
                "SIP_ASTERISK_IP=192.168.1.100\n"
                "SIP_ASTERISK_PORT=5060\n"
                "SIP_DOMAIN=192.168.1.100\n"
                "SIP_RAMAL=1002\n"
                "SIP_USUARIO_AUTH=1002\n"
                "SIP_SENHA=\n"
            )
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write(initial_content)
            return True
    except Exception:
        return False


def get_subprocess_env(extra_env: Optional[dict] = None) -> dict:
    """
    Prepara o dicionário de variáveis de ambiente para subprocessos do SIPp,
    garantindo que o diretório bin/sipp (com cygwin1.dll e DLLs correlatas)
    esteja presente no PATH do sistema.
    """
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    if sys.platform == "win32" and os.path.exists(SIPP_DIR):
        current_path = env.get("PATH", "")
        if SIPP_DIR not in current_path:
            env["PATH"] = SIPP_DIR + os.pathsep + current_path
        env["CYGWIN"] = "nodosfilewarning"

    return env

