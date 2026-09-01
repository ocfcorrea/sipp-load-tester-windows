"""
Paths Manager - Gerenciador centralizado de diretórios e caminhos de recursos.
Garante que todos os módulos acessem arquivos com caminhos absolutos baseados na raiz do projeto,
evitando erros de diretório de trabalho relativo (Current Working Directory) entre diferentes máquinas.
"""

import os
import sys
import shutil
from typing import Optional

# Detecta se está rodando como executável congelado (.exe compilado via PyInstaller)
if getattr(sys, "frozen", False):
    # Pasta temporária de recursos internos embutidos no .exe
    BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(sys.executable)))
    # Pasta onde o arquivo .exe reside no disco (para persistir config.json e .env)
    BASE_DIR = os.path.abspath(os.path.dirname(sys.executable))
else:
    BUNDLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    BASE_DIR = BUNDLE_DIR

# Diretórios principais
CORE_DIR = os.path.join(BUNDLE_DIR, "core")
GUI_DIR = os.path.join(BUNDLE_DIR, "gui")
BIN_DIR = os.path.join(BUNDLE_DIR, "bin")
SIPP_DIR = os.path.join(BIN_DIR, "sipp")
SCENARIOS_DIR = os.path.join(BUNDLE_DIR, "scenarios")
PCAP_DIR = os.path.join(BUNDLE_DIR, "pcap")

# Arquivos de configuração e dados persistentes (salvos na pasta do .exe)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")
ENV_EXAMPLE_FILE = os.path.join(BUNDLE_DIR, ".env.example")

# Diretório de dependências offline (vendored)
LIB_DIR = os.path.join(BUNDLE_DIR, "lib")

# Injeta automaticamente lib/ no sys.path para execução offline imediata
if os.path.exists(LIB_DIR) and LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

# Executável SIPp padrão para Windows
DEFAULT_SIPP_EXE = os.path.join(SIPP_DIR, "sipp.exe" if sys.platform == "win32" else "sipp")
DEFAULT_PCAP_FILE = os.path.join(PCAP_DIR, "g711a.pcap")


def get_project_path(*subpaths: str) -> str:
    """Retorna o caminho absoluto de um arquivo ou diretório a partir da raiz de execução."""
    return os.path.normpath(os.path.join(BASE_DIR, *subpaths))


def resolve_scenario(filename: str) -> str:
    """
    Resolve o caminho absoluto de um arquivo de cenário XML ou template.
    Busca primeiro em BUNDLE_DIR/scenarios, depois em BASE_DIR/scenarios, e na raiz.
    """
    candidates = [
        os.path.join(SCENARIOS_DIR, filename),
        os.path.join(BASE_DIR, "scenarios", filename),
        os.path.join(BUNDLE_DIR, filename),
        os.path.join(BASE_DIR, filename)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
        
    return os.path.join(SCENARIOS_DIR, filename)


def resolve_pcap(filename: str = "g711a.pcap") -> str:
    """Resolve o caminho absoluto de um arquivo PCAP."""
    if not filename:
        return DEFAULT_PCAP_FILE
        
    if os.path.isabs(filename) and os.path.exists(filename):
        return filename

    candidates = [
        os.path.join(PCAP_DIR, os.path.basename(filename)),
        os.path.join(BASE_DIR, "pcap", os.path.basename(filename)),
        os.path.join(BUNDLE_DIR, filename),
        os.path.join(BASE_DIR, filename)
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
        
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
                "SIP_ASTERISK_IP=192.168.0.1\n"
                "SIP_ASTERISK_PORT=5060\n"
                "SIP_DOMAIN=192.168.0.1\n"
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

