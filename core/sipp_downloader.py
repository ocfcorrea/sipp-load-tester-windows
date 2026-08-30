"""
SIPp Downloader & Locator - Utilitário para localizar, validar e auxiliar o download do SIPp para Windows.
"""

import os
import shutil
import subprocess
import urllib.request
import zipfile
from typing import Tuple, Optional


class SippLocator:
    """Detecta a presença do executável SIPp e gerencia o ambiente de execução."""

    COMMON_WINDOWS_PATHS = [
        "bin/sipp/sipp.exe",
        "bin\\sipp\\sipp.exe",
        "sipp.exe",
        "./sipp.exe",
        "C:\\Program Files\\SIPp\\sipp.exe",
        "C:\\Program Files (x86)\\SIPp\\sipp.exe",
        "C:\\cygwin64\\bin\\sipp.exe",
        "C:\\cygwin\\bin\\sipp.exe",
        "sipp",
    ]

    @staticmethod
    def find_sipp(configured_path: str = "") -> Optional[str]:
        """Procura o executável SIPp no caminho configurado, diretório local ou PATH."""
        # 1. Tenta o caminho configurado
        if configured_path and os.path.exists(configured_path):
            return configured_path
        
        if configured_path:
            which_res = shutil.which(configured_path)
            if which_res:
                return which_res

        # 2. Tenta os caminhos comuns
        for path in SippLocator.COMMON_WINDOWS_PATHS:
            if os.path.exists(path):
                return path
            which_res = shutil.which(path)
            if which_res:
                return which_res

        # 3. Tenta comando padrão 'sipp' ou 'sipp.exe' no PATH
        for cmd in ["sipp.exe", "sipp"]:
            which_res = shutil.which(cmd)
            if which_res:
                return which_res

        return None

    @staticmethod
    def check_sipp_version(binary_path: str) -> Tuple[bool, str]:
        """Executa 'sipp -v' e retorna a versão e status de suporte a PCAP."""
        if not binary_path:
            return False, "Caminho do executável SIPp não informado."
            
        try:
            # Em Windows, se for arquivo Linux ELF, pode falhar se não executado no WSL
            result = subprocess.run(
                [binary_path, "-v"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            output = (result.stdout + "\n" + result.stderr).strip()
            first_line = output.splitlines()[0] if output else "Versão desconhecida"
            has_pcap = "pcap" in output.lower()
            
            status_msg = f"{first_line} | Suporte PCAP: {'SIM (Habilitado)' if has_pcap else 'NÃO'}"
            return True, status_msg
        except FileNotFoundError:
            return False, f"Executável não encontrado em: {binary_path}"
        except OSError as e:
            if getattr(e, 'winerror', 0) == 193:
                return False, f"O arquivo '{binary_path}' é um binário Linux (ELF). No Windows, use 'sipp.exe' ou execute via WSL/Cygwin."
            return False, f"Erro ao executar SIPp: {e}"
        except Exception as e:
            return False, f"Erro ao verificar versão: {e}"

    @staticmethod
    def download_sipp_windows(dest_dir: str = "sipp_win", progress_callback=None) -> Tuple[bool, str]:
        """
        Auxilia no download/configuração do SIPp para Windows.
        """
        os.makedirs(dest_dir, exist_ok=True)
        # URL oficial do repositório / build
        url = "https://downloads.sourceforge.net/project/sipp/sipp/3.2/sipp-win32-3.2-setup.exe"
        installer_path = os.path.join(dest_dir, "sipp-installer.exe")
        
        try:
            if progress_callback:
                progress_callback("Baixando instalador do SIPp para Windows...", 0.1)

            # Usa curl do Windows ou urllib com User-Agent
            curl_bin = shutil.which("curl.exe") or shutil.which("curl")
            if curl_bin:
                cmd = [curl_bin, "-L", "-o", installer_path, url]
                subprocess.run(cmd, check=True, timeout=60)
            else:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as resp, open(installer_path, "wb") as out:
                    shutil.copyfileobj(resp, out)

            if progress_callback:
                progress_callback("Download concluído. Executando instalador...", 0.7)

            # Executa instalador
            return True, f"Instalador baixado com sucesso em '{installer_path}'. Execute-o para instalar o SIPp no Windows."
        except Exception as e:
            return False, f"Falha ao baixar SIPp: {e}"
