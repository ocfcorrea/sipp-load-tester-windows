"""
SIP Client - Cliente SIP nativo em Python para teste de conectividade e registro Digest (RFC 3261 / RFC 2617).
Não depende de binários externos, OpenSSL ou DLLs do sistema.
"""

import socket
import hashlib
import re
import uuid
import time
from typing import Tuple, Optional, Dict, Any


class SipClient:
    """Cliente SIP leve para testes de registro e autenticação Digest."""

    @staticmethod
    def parse_sip_message(raw_data: str) -> Dict[str, Any]:
        """Faz o parsing básico de uma mensagem SIP recebida."""
        lines = raw_data.splitlines()
        if not lines:
            return {}

        status_line = lines[0].strip()
        parts = status_line.split(" ", 2)
        status_code = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0
        reason = parts[2] if len(parts) >= 3 else ""

        headers = {}
        for line in lines[1:]:
            line = line.strip()
            if not line:
                break
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()

        return {
            "status_line": status_line,
            "status_code": status_code,
            "reason": reason,
            "headers": headers,
            "raw": raw_data
        }

    @staticmethod
    def parse_auth_challenge(auth_header: str) -> Dict[str, str]:
        """Extrai os parâmetros do cabeçalho WWW-Authenticate ou Proxy-Authenticate."""
        params = {}
        # Remove 'Digest ' se presente
        clean = re.sub(r'^[Dd]igest\s+', '', auth_header.strip())
        
        # Regex para capturar chave="valor" ou chave=valor
        matches = re.findall(r'(\w+)=(?:"([^"]*)"|([^,\s]*))', clean)
        for k, v1, v2 in matches:
            params[k.lower()] = v1 if v1 is not None and v1 != '' else v2
            
        return params

    @staticmethod
    def compute_digest_response(
        username: str,
        realm: str,
        password: str,
        method: str,
        uri: str,
        nonce: str,
        qop: Optional[str] = None,
        nc: str = "00000001",
        cnonce: Optional[str] = None
    ) -> str:
        """Calcula o hash MD5 da resposta de autenticação Digest (RFC 2617)."""
        ha1_raw = f"{username}:{realm}:{password}"
        ha1 = hashlib.md5(ha1_raw.encode("utf-8")).hexdigest()

        ha2_raw = f"{method}:{uri}"
        ha2 = hashlib.md5(ha2_raw.encode("utf-8")).hexdigest()

        if qop and "auth" in qop.lower():
            cnonce = cnonce or uuid.uuid4().hex[:8]
            resp_raw = f"{ha1}:{nonce}:{nc}:{cnonce}:auth:{ha2}"
        else:
            resp_raw = f"{ha1}:{nonce}:{ha2}"

        return hashlib.md5(resp_raw.encode("utf-8")).hexdigest()

    @classmethod
    def test_register(
        cls,
        host: str,
        port: int = 5060,
        ramal: str = "1002",
        auth_user: str = "",
        password: str = "",
        domain: str = "",
        transport: str = "u1",
        timeout: float = 6.0,
        local_ip: str = ""
    ) -> Tuple[bool, int, str, float]:
        """
        Executa um fluxo completo de SIP REGISTER:
        1. Envia REGISTER sem credenciais
        2. Recebe 401/407 com desafio Digest
        3. Calcula a resposta MD5 e envia REGISTER com Authorization
        4. Recebe 200 OK
        Retorna (sucesso, status_code, mensagem_explicativa, latencia_segundos).
        """
        domain = domain.strip() or host
        auth_user = auth_user.strip() or ramal
        is_tcp = transport.lower() in ["t1", "tcp"]
        start_time = time.time()

        sock = None
        try:
            if is_tcp:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                sock.connect((host, port))
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(timeout)

            # Obtém IP local
            if local_ip:
                my_ip = local_ip
            else:
                try:
                    # Abre socket fictício para determinar a interface de saída
                    s_probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s_probe.connect((host, port if port > 0 else 5060))
                    my_ip = s_probe.getsockname()[0]
                    s_probe.close()
                except Exception:
                    my_ip = "127.0.0.1"

            my_port = sock.getsockname()[1] if is_tcp else (sock.getsockname()[1] if sock.getsockname()[1] != 0 else 5060)

            call_id = f"{uuid.uuid4().hex}@{my_ip}"
            from_tag = uuid.uuid4().hex[:8]
            branch_1 = f"z9hG4bK-{uuid.uuid4().hex[:8]}"

            # 1. Primeiro REGISTER (sem auth)
            reg_msg_1 = (
                f"REGISTER sip:{domain} SIP/2.0\r\n"
                f"Via: SIP/2.0/{'TCP' if is_tcp else 'UDP'} {my_ip}:{my_port};branch={branch_1};rport\r\n"
                f"Max-Forwards: 70\r\n"
                f"From: \"{ramal}\" <sip:{ramal}@{domain}>;tag={from_tag}\r\n"
                f"To: <sip:{ramal}@{domain}>\r\n"
                f"Call-ID: {call_id}\r\n"
                f"CSeq: 1 REGISTER\r\n"
                f"Contact: <sip:{ramal}@{my_ip}:{my_port};transport={'tcp' if is_tcp else 'udp'}>\r\n"
                f"Expires: 3600\r\n"
                f"User-Agent: SIPp-Load-Tester-Pro\r\n"
                f"Content-Length: 0\r\n\r\n"
            )

            if is_tcp:
                sock.sendall(reg_msg_1.encode("utf-8"))
                resp_data_1 = sock.recv(4096).decode("utf-8", errors="ignore")
            else:
                sock.sendto(reg_msg_1.encode("utf-8"), (host, port))
                resp_data_1, _ = sock.recvfrom(4096)
                resp_data_1 = resp_data_1.decode("utf-8", errors="ignore")

            parsed_1 = cls.parse_sip_message(resp_data_1)
            code_1 = parsed_1.get("status_code", 0)

            # Se o servidor não exigiu autenticação e já retornou 200 OK
            if code_1 == 200:
                duration = round(time.time() - start_time, 2)
                return True, 200, f"Registrado com Sucesso (200 OK em {duration}s - Sem desafio)", duration

            # Se recebeu 401 ou 407 (Desafio de autenticação Digest)
            if code_1 in [401, 407]:
                auth_hdr = (
                    parsed_1["headers"].get("www-authenticate") or
                    parsed_1["headers"].get("proxy-authenticate") or
                    ""
                )
                if not auth_hdr:
                    return False, code_1, f"Servidor retornou {code_1} sem cabeçalho WWW-Authenticate.", round(time.time() - start_time, 2)

                auth_params = cls.parse_auth_challenge(auth_hdr)
                realm = auth_params.get("realm", domain)
                nonce = auth_params.get("nonce", "")
                qop = auth_params.get("qop")
                opaque = auth_params.get("opaque")
                cnonce = uuid.uuid4().hex[:8]
                nc = "00000001"
                uri = f"sip:{domain}"

                digest_resp = cls.compute_digest_response(
                    username=auth_user,
                    realm=realm,
                    password=password,
                    method="REGISTER",
                    uri=uri,
                    nonce=nonce,
                    qop=qop,
                    nc=nc,
                    cnonce=cnonce
                )

                # Monta cabeçalho Authorization
                auth_val = (
                    f'Digest username="{auth_user}", '
                    f'realm="{realm}", '
                    f'nonce="{nonce}", '
                    f'uri="{uri}", '
                    f'response="{digest_resp}", '
                    f'algorithm=MD5'
                )
                if qop and "auth" in qop.lower():
                    auth_val += f', cnonce="{cnonce}", qop=auth, nc={nc}'
                if opaque:
                    auth_val += f', opaque="{opaque}"'

                auth_header_name = "Proxy-Authorization" if code_1 == 407 else "Authorization"
                branch_2 = f"z9hG4bK-{uuid.uuid4().hex[:8]}"

                # 2. Segundo REGISTER (com credenciais Digest calculadas)
                reg_msg_2 = (
                    f"REGISTER sip:{domain} SIP/2.0\r\n"
                    f"Via: SIP/2.0/{'TCP' if is_tcp else 'UDP'} {my_ip}:{my_port};branch={branch_2};rport\r\n"
                    f"Max-Forwards: 70\r\n"
                    f"From: \"{ramal}\" <sip:{ramal}@{domain}>;tag={from_tag}\r\n"
                    f"To: <sip:{ramal}@{domain}>\r\n"
                    f"Call-ID: {call_id}\r\n"
                    f"CSeq: 2 REGISTER\r\n"
                    f"Contact: <sip:{ramal}@{my_ip}:{my_port};transport={'tcp' if is_tcp else 'udp'}>\r\n"
                    f"{auth_header_name}: {auth_val}\r\n"
                    f"Expires: 3600\r\n"
                    f"User-Agent: SIPp-Load-Tester-Pro\r\n"
                    f"Content-Length: 0\r\n\r\n"
                )

                if is_tcp:
                    sock.sendall(reg_msg_2.encode("utf-8"))
                    resp_data_2 = sock.recv(4096).decode("utf-8", errors="ignore")
                else:
                    sock.sendto(reg_msg_2.encode("utf-8"), (host, port))
                    resp_data_2, _ = sock.recvfrom(4096)
                    resp_data_2 = resp_data_2.decode("utf-8", errors="ignore")

                parsed_2 = cls.parse_sip_message(resp_data_2)
                code_2 = parsed_2.get("status_code", 0)
                reason_2 = parsed_2.get("reason", "")
                duration = round(time.time() - start_time, 2)

                if code_2 == 200:
                    return True, 200, f"Registrado com Sucesso (200 OK em {duration}s)", duration
                elif code_2 in [401, 407]:
                    return False, code_2, "Falha de Autenticação (Usuário ou Senha incorretos)", duration
                elif code_2 == 403:
                    return False, 403, "Acesso Proibido (403 Forbidden - Ramal não autorizado)", duration
                elif code_2 == 404:
                    return False, 404, "Ramal não encontrado no PBX (404 Not Found)", duration
                else:
                    return False, code_2, f"Erro SIP {code_2} ({reason_2})", duration

            duration = round(time.time() - start_time, 2)
            return False, code_1, f"Resposta inesperada do servidor: {code_1} {parsed_1.get('reason', '')}", duration

        except socket.timeout:
            return False, 0, f"Tempo esgotado (Timeout: Servidor {host}:{port} não respondeu em {timeout}s)", round(time.time() - start_time, 2)
        except ConnectionRefusedError:
            return False, 0, f"Conexão recusada em {host}:{port}. Verifique se o Asterisk está rodando.", round(time.time() - start_time, 2)
        except Exception as e:
            return False, 0, f"Erro de comunicação de rede: {e}", round(time.time() - start_time, 2)
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
