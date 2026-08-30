"""
Security Layer - Validação de entradas, sanitização contra SIP Injection / Command Injection,
mascaramento de credenciais em logs e gerenciamento seguro de arquivos temporários.
"""

import os
import re
from typing import Tuple, Optional, Any


class SecurityValidator:
    """Camada de segurança e validação de parâmetros."""

    # Regex para validação estrita de Host/IP/FQDN
    IP_REGEX = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    FQDN_REGEX = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-_]{1,63}(?<!-)(?:\.(?!-)[A-Za-z0-9-_]{1,63}(?<!-))*$")

    # Caracteres perigosos para injeção de cabeçalho SIP (CRLF) ou comando
    SIP_FORBIDDEN_CHARS = re.compile(r"[\r\n\x00]")
    DANGEROUS_CMD_CHARS = re.compile(r"[;&|`$><]")

    @classmethod
    def validate_host(cls, host: str) -> Tuple[bool, str]:
        """Valida se o endereço informado é um IP ou FQDN seguro."""
        if not host or not isinstance(host, str):
            return False, "Endereço do host não pode ser vazio."
        
        host_clean = host.strip()
        if cls.SIP_FORBIDDEN_CHARS.search(host_clean):
            return False, "Endereço contém caracteres inválidos (CRLF)."
        
        if cls.IP_REGEX.match(host_clean) or cls.FQDN_REGEX.match(host_clean) or host_clean == "localhost":
            return True, host_clean
        
        return False, f"Formato de IP ou FQDN inválido: '{host_clean}'"

    @classmethod
    def validate_port(cls, port: Any) -> Tuple[bool, int]:
        """Valida se a porta está entre 1 e 65535."""
        try:
            p = int(port)
            if 1 <= p <= 65535:
                return True, p
            return False, 0
        except (ValueError, TypeError):
            return False, 0

    @classmethod
    def validate_sip_user(cls, user: str, field_name: str = "Ramal") -> Tuple[bool, str]:
        """Valida usuário/ramal SIP contra injeção de cabeçalhos."""
        if not user or not isinstance(user, str):
            return False, f"{field_name} não pode ser vazio."
        
        user_clean = user.strip()
        if cls.SIP_FORBIDDEN_CHARS.search(user_clean):
            return False, f"{field_name} contém quebras de linha ou caracteres proibidos."
        
        # Permitido caracteres alfanuméricos, ponto, traço, sublinhado e $
        if not re.match(r"^[a-zA-Z0-9_\-\.\$\@]+$", user_clean):
            return False, f"{field_name} contém caracteres especiais não suportados."
        
        return True, user_clean

    @classmethod
    def validate_destination_number(cls, dest: str) -> Tuple[bool, str]:
        """Valida número de destino para discagem."""
        if not dest or not isinstance(dest, str):
            return False, "Destino não pode ser vazio."
        
        dest_clean = dest.strip()
        if cls.SIP_FORBIDDEN_CHARS.search(dest_clean):
            return False, "Destino contém caracteres proibidos."
        
        if not re.match(r"^[0-9a-zA-Z\*\#\+\-\_]+$", dest_clean):
            return False, f"Destino '{dest_clean}' contém caracteres inválidos para discagem."
        
        return True, dest_clean

    @classmethod
    def mask_credentials(cls, text: str, password: str = "") -> str:
        """Mascara senhas e credenciais sensíveis em saídas de log."""
        if not text:
            return ""
        
        masked = text
        if password and len(password) >= 2:
            masked = masked.replace(password, "******")
        
        # Mascara senhas em comandos com -ap
        masked = re.sub(r"(-ap\s+)([^\s]+)", r"\1******", masked)
        masked = re.sub(r"(password=[\"']?)([^\"'\s>]+)([\"']?)", r"\1******\3", masked)
        masked = re.sub(r"(;[^\n;]+;)([^\n;]+)(\n|$)", r";******;\2\3", masked)
        
        return masked

    @classmethod
    def secure_delete_file(cls, file_path: str):
        """Remove arquivos temporários contendo credenciais de forma segura."""
        if not file_path or not os.path.exists(file_path):
            return
        
        try:
            # Sobrescreve com zeros antes de deletar
            size = os.path.getsize(file_path)
            with open(file_path, "wb") as f:
                f.write(b"\x00" * size)
            os.remove(file_path)
        except Exception:
            try:
                os.remove(file_path)
            except Exception:
                pass

    @classmethod
    def safe_path(cls, path: str, allowed_base_dir: Optional[str] = None) -> bool:
        """Verifica se o caminho do arquivo evita Path Traversal."""
        if not path:
            return False
        
        abs_path = os.path.abspath(path)
        if allowed_base_dir:
            abs_base = os.path.abspath(allowed_base_dir)
            return abs_path.startswith(abs_base)
        return True
