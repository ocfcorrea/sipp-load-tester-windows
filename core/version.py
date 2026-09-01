"""
Version Manager - Gerenciamento e cálculo de versão dinâmica do aplicativo.
Combina versionamento semântico (SemVer) com contagem de commits do Git
para gerar releases numéricas auto-incrementais a cada commit.
"""

import os
import json
import subprocess
from typing import Dict, Any

VERSION_MAJOR = 2
VERSION_MINOR = 0
VERSION_FALLBACK_BUILD = 8

APP_NAME = "SIPp Load Tester Pro"

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_JSON_FILE = os.path.join(ROOT_DIR, "version.json")


def _run_git_cmd(args: list) -> str:
    """Executa comando Git silenciosamente no repositório."""
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=ROOT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return ""


def get_git_commit_count() -> int:
    """Retorna o número total de commits do repositório Git."""
    out = _run_git_cmd(["rev-list", "--count", "HEAD"])
    if out.isdigit():
        return int(out)
    return VERSION_FALLBACK_BUILD


def get_git_short_hash() -> str:
    """Retorna o hash abreviado do último commit."""
    out = _run_git_cmd(["rev-parse", "--short", "HEAD"])
    return out if out else "latest"


def get_version_info() -> Dict[str, Any]:
    """
    Retorna o dicionário completo com informações de versão.
    Prioriza arquivo version.json estático (se empacotado no .exe), 
    caso contrário consulta o Git local em tempo real.
    """
    # 1. Se existir version.json estático (gerado no build do PyInstaller)
    if os.path.exists(VERSION_JSON_FILE):
        try:
            with open(VERSION_JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "version" in data:
                    return data
        except Exception:
            pass

    # 2. Consulta Git dinâmico
    build_num = get_git_commit_count()
    commit_hash = get_git_short_hash()
    version_str = f"{VERSION_MAJOR}.{VERSION_MINOR}.{build_num}"

    return {
        "app_name": APP_NAME,
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "build": build_num,
        "commit": commit_hash,
        "version": version_str,
        "release_tag": f"v{version_str}",
        "display_title": f"{APP_NAME} v{version_str}"
    }


def save_version_file(target_path: str = VERSION_JSON_FILE) -> str:
    """Gera o arquivo version.json com a versão atual para empacotamento do .exe."""
    info = get_version_info()
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)
    return info["release_tag"]


def get_version() -> str:
    """Retorna apenas a string de versão (ex: '2.0.8')."""
    return get_version_info()["version"]


def get_version_tag() -> str:
    """Retorna a tag de versão (ex: 'v2.0.8')."""
    return get_version_info()["release_tag"]


def get_app_title() -> str:
    """Retorna o título formatado da janela principal."""
    return get_version_info()["display_title"]
