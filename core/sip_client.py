"""
SIP Client - Cliente SIP nativo em Python para teste de conectividade e registro Digest (RFC 3261 / RFC 2617).
Não depende de binários externos, OpenSSL ou DLLs do sistema.
"""

import socket
import hashlib
import re
import uuid
import time
from typing import Tuple, Optional, Dict, Any, List


import os
import struct

_PCAP_CACHE: Dict[str, List[bytes]] = {}


class SipClient:
    """Cliente SIP leve para testes de registro e autenticação Digest com streaming RTP."""

    @staticmethod
    def extract_pcap_rtp_packets(pcap_path: str) -> List[bytes]:
        """Extrai os pacotes RTP de um arquivo .pcap Ethernet/IP/UDP e mantém em cache de memória."""
        if not pcap_path:
            return []
        
        abs_path = os.path.abspath(pcap_path)
        if abs_path in _PCAP_CACHE:
            return _PCAP_CACHE[abs_path]

        if not os.path.exists(abs_path):
            return []

        packets = []
        try:
            with open(abs_path, "rb") as f:
                ghdr = f.read(24)
                if len(ghdr) < 24:
                    return []
                magic = struct.unpack("<I", ghdr[:4])[0]
                endian = "<" if magic == 0xa1b2c3d4 else ">"

                while True:
                    phdr = f.read(16)
                    if len(phdr) < 16:
                        break
                    ts_s, ts_u, incl_len, orig_len = struct.unpack(endian + "IIII", phdr)
                    data = f.read(incl_len)

                    # Ethernet (14 bytes) + IPv4 (min 20 bytes) + UDP (8 bytes) = 42 bytes
                    if len(data) > 42:
                        eth_type = struct.unpack(">H", data[12:14])[0]
                        if eth_type == 0x0800:  # IPv4
                            ihl = (data[14] & 0x0F) * 4
                            udp_off = 14 + ihl
                            if len(data) >= udp_off + 8:
                                udp_len = struct.unpack(">H", data[udp_off+4:udp_off+6])[0]
                                rtp_payload = data[udp_off+8:udp_off+udp_len]
                                if len(rtp_payload) >= 12:
                                    packets.append(rtp_payload)

            _PCAP_CACHE[abs_path] = packets
            return packets
        except Exception:
            return []

    @staticmethod
    def parse_sdp_media(raw_data: str, default_ip: str) -> Tuple[str, int]:
        """Extrai o IP de mídia e porta RTP do SDP retornado no 200 OK do PBX."""
        remote_ip = default_ip
        remote_port = 0

        for line in raw_data.splitlines():
            line = line.strip()
            if line.startswith("c=IN IP4 "):
                remote_ip = line.split("c=IN IP4 ")[1].strip()
            elif line.startswith("m=audio "):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    remote_port = int(parts[1])

        return remote_ip, remote_port

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
                my_ip = local_ip or sock.getsockname()[0]
                my_port = sock.getsockname()[1]
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(timeout)
                # No Windows, é obrigatório efetuar o bind antes de chamar getsockname para evitar WinError 10022
                sock.bind(('', 0))
                my_port = sock.getsockname()[1]

                if local_ip:
                    my_ip = local_ip
                else:
                    try:
                        # Abre socket fictício para determinar a interface de saída correta
                        s_probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s_probe.connect((host, port if port > 0 else 5060))
                        my_ip = s_probe.getsockname()[0]
                        s_probe.close()
                    except Exception:
                        my_ip = "127.0.0.1"

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
        except ConnectionResetError:
            return False, 0, f"Porta SIP {port} fechada em {host}. Verifique se o Asterisk está ativo e escutando nessa porta.", round(time.time() - start_time, 2)
        except OSError as e:
            if getattr(e, 'winerror', 0) == 10054:
                return False, 0, f"Porta SIP {port} fechada em {host}. Verifique se o Asterisk está ativo e escutando nessa porta.", round(time.time() - start_time, 2)
            return False, 0, f"Erro de rede: {e}", round(time.time() - start_time, 2)
        except Exception as e:
            return False, 0, f"Erro inesperado no registro: {e}", round(time.time() - start_time, 2)
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    @classmethod
    def single_call(
        cls,
        host: str,
        port: int = 5060,
        ramal: str = "1002",
        auth_user: str = "",
        password: str = "",
        destination: str = "22221864",
        domain: str = "",
        transport: str = "u1",
        duration_sec: float = 30.0,
        local_ip: str = "",
        media_port: int = 6000,
        pcap_file: str = "pcap/g711a.pcap",
        log_callback: Optional[Any] = None,
        status_callback: Optional[Any] = None,
        stop_event: Optional[Any] = None
    ) -> Tuple[bool, int, str]:
        """
        Executa uma chamada SIP completa de teste (INVITE -> 401/407 Digest -> 200 OK -> ACK -> Pausa/RTP -> BYE -> 200 OK).
        100% nativo em Python puro, com suporte a MD5 Digest e logs em tempo real.
        """
        def _log(msg: str, level: str = "INFO"):
            if log_callback:
                log_callback(f"[CHAMADA ÚNICA] {msg}", level)

        def _status(msg: str):
            if status_callback:
                status_callback(msg)

        domain = domain.strip() or host
        auth_user = auth_user.strip() or ramal
        is_tcp = transport.lower() in ["t1", "tcp"]
        start_time = time.time()
        sock = None

        try:
            if is_tcp:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5.0)
                sock.connect((host, port))
                my_ip = local_ip or sock.getsockname()[0]
                my_port = sock.getsockname()[1]
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(5.0)
                sock.bind(('', 0))
                my_port = sock.getsockname()[1]

                if local_ip:
                    my_ip = local_ip
                else:
                    try:
                        s_probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s_probe.connect((host, port if port > 0 else 5060))
                        my_ip = s_probe.getsockname()[0]
                        s_probe.close()
                    except Exception:
                        my_ip = "127.0.0.1"

            call_id = f"{uuid.uuid4().hex}@{my_ip}"
            from_tag = uuid.uuid4().hex[:8]
            branch_1 = f"z9hG4bK-{uuid.uuid4().hex[:8]}"

            # SDP Offer (PCMA 8kHz / PCMU)
            sdp_body = (
                f"v=0\r\n"
                f"o=sipp-pro {int(start_time)} {int(start_time)} IN IP4 {my_ip}\r\n"
                f"s=SIPp-Load-Tester-Pro\r\n"
                f"c=IN IP4 {my_ip}\r\n"
                f"t=0 0\r\n"
                f"m=audio {media_port} RTP/AVP 8 0 101\r\n"
                f"a=rtpmap:8 PCMA/8000\r\n"
                f"a=rtpmap:0 PCMU/8000\r\n"
                f"a=rtpmap:101 telephone-event/8000\r\n"
                f"a=fmtp:101 0-15\r\n"
                f"a=sendrecv\r\n"
            )

            # 1. Primeiro INVITE
            invite_msg_1 = (
                f"INVITE sip:{destination}@{domain} SIP/2.0\r\n"
                f"Via: SIP/2.0/{'TCP' if is_tcp else 'UDP'} {my_ip}:{my_port};branch={branch_1};rport\r\n"
                f"Max-Forwards: 70\r\n"
                f"From: \"{ramal}\" <sip:{ramal}@{domain}>;tag={from_tag}\r\n"
                f"To: <sip:{destination}@{domain}>\r\n"
                f"Call-ID: {call_id}\r\n"
                f"CSeq: 1 INVITE\r\n"
                f"Contact: <sip:{ramal}@{my_ip}:{my_port};transport={'tcp' if is_tcp else 'udp'}>\r\n"
                f"User-Agent: SIPp-Load-Tester-Pro\r\n"
                f"Content-Type: application/sdp\r\n"
                f"Content-Length: {len(sdp_body.encode('utf-8'))}\r\n\r\n"
                f"{sdp_body}"
            )

            _log(f"➔ Enviando INVITE inicial para {destination}@{domain} ({host}:{port})...", "INFO")
            _status(f"Disparando INVITE ➔ {destination}...")

            if is_tcp:
                sock.sendall(invite_msg_1.encode("utf-8"))
            else:
                sock.sendto(invite_msg_1.encode("utf-8"), (host, port))

            # Loop de recepção de respostas provisórias e definitivas
            current_cseq = 1
            authenticated = False
            peer_to_tag = ""

            while True:
                if stop_event and stop_event.is_set():
                    _log("⏹️ Cancelamento solicitado pelo operador antes do atendimento.", "WARNING")
                    return False, 0, "Cancelado pelo operador"

                try:
                    if is_tcp:
                        resp_data = sock.recv(4096).decode("utf-8", errors="ignore")
                    else:
                        resp_data, _ = sock.recvfrom(4096)
                        resp_data = resp_data.decode("utf-8", errors="ignore")
                except socket.timeout:
                    _log(f"⚠️ Timeout aguardando resposta SIP do PBX ({host}:{port}).", "ERROR")
                    _status("Timeout de Resposta")
                    return False, 0, "Timeout de resposta do PBX"

                parsed = cls.parse_sip_message(resp_data)
                code = parsed.get("status_code", 0)
                reason = parsed.get("reason", "")
                
                # Extrai tag do cabeçalho To
                to_hdr = parsed.get("headers", {}).get("to", "")
                if "tag=" in to_hdr:
                    peer_to_tag = to_hdr.split("tag=", 1)[1].split(";", 1)[0].strip()

                _log(f"◄ Recebido: SIP {code} {reason}", "DEBUG" if code == 100 else "INFO")

                if code == 100:
                    _status("100 Trying (PBX processando)...")
                    continue

                if code in [180, 183]:
                    _status(f"🔔 Chamando ({code} {reason})...")
                    continue

                # Se desafiado com 401 ou 407 (Digest Authentication)
                if code in [401, 407] and not authenticated:
                    _log(f"🔐 Desafio de autenticação recebido ({code} {reason}). Calculando hash Digest MD5...", "INFO")
                    _status("Autenticando via Digest MD5...")

                    # Envia ACK ao desafio
                    ack_branch = f"z9hG4bK-{uuid.uuid4().hex[:8]}"
                    to_field = f"<sip:{destination}@{domain}>" + (f";tag={peer_to_tag}" if peer_to_tag else "")
                    ack_msg = (
                        f"ACK sip:{destination}@{domain} SIP/2.0\r\n"
                        f"Via: SIP/2.0/{'TCP' if is_tcp else 'UDP'} {my_ip}:{my_port};branch={ack_branch};rport\r\n"
                        f"Max-Forwards: 70\r\n"
                        f"From: \"{ramal}\" <sip:{ramal}@{domain}>;tag={from_tag}\r\n"
                        f"To: {to_field}\r\n"
                        f"Call-ID: {call_id}\r\n"
                        f"CSeq: {current_cseq} ACK\r\n"
                        f"Content-Length: 0\r\n\r\n"
                    )
                    if is_tcp:
                        sock.sendall(ack_msg.encode("utf-8"))
                    else:
                        sock.sendto(ack_msg.encode("utf-8"), (host, port))

                    # Parse do desafio
                    auth_hdr = (
                        parsed["headers"].get("www-authenticate") or
                        parsed["headers"].get("proxy-authenticate") or
                        ""
                    )
                    auth_params = cls.parse_auth_challenge(auth_hdr)
                    realm = auth_params.get("realm", domain)
                    nonce = auth_params.get("nonce", "")
                    qop = auth_params.get("qop")
                    opaque = auth_params.get("opaque")
                    cnonce = uuid.uuid4().hex[:8]
                    nc = "00000001"
                    uri = f"sip:{destination}@{domain}"

                    digest_resp = cls.compute_digest_response(
                        username=auth_user,
                        realm=realm,
                        password=password,
                        method="INVITE",
                        uri=uri,
                        nonce=nonce,
                        qop=qop,
                        nc=nc,
                        cnonce=cnonce
                    )

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

                    auth_header_name = "Proxy-Authorization" if code == 407 else "Authorization"
                    branch_2 = f"z9hG4bK-{uuid.uuid4().hex[:8]}"
                    current_cseq = 2
                    authenticated = True

                    # 2. Segundo INVITE autenticado
                    invite_msg_2 = (
                        f"INVITE sip:{destination}@{domain} SIP/2.0\r\n"
                        f"Via: SIP/2.0/{'TCP' if is_tcp else 'UDP'} {my_ip}:{my_port};branch={branch_2};rport\r\n"
                        f"Max-Forwards: 70\r\n"
                        f"From: \"{ramal}\" <sip:{ramal}@{domain}>;tag={from_tag}\r\n"
                        f"To: <sip:{destination}@{domain}>\r\n"
                        f"Call-ID: {call_id}\r\n"
                        f"CSeq: 2 INVITE\r\n"
                        f"Contact: <sip:{ramal}@{my_ip}:{my_port};transport={'tcp' if is_tcp else 'udp'}>\r\n"
                        f"{auth_header_name}: {auth_val}\r\n"
                        f"User-Agent: SIPp-Load-Tester-Pro\r\n"
                        f"Content-Type: application/sdp\r\n"
                        f"Content-Length: {len(sdp_body.encode('utf-8'))}\r\n\r\n"
                        f"{sdp_body}"
                    )

                    _log(f"➔ Enviando INVITE com credenciais Digest (Auth User: {auth_user})...", "INFO")
                    if is_tcp:
                        sock.sendall(invite_msg_2.encode("utf-8"))
                    else:
                        sock.sendto(invite_msg_2.encode("utf-8"), (host, port))
                    continue

                # Se chamada atendida (200 OK)
                if code == 200:
                    setup_time = round(time.time() - start_time, 2)
                    _log(f"🎉 SUCESSO: Chamada atendida (200 OK) em {setup_time}s! Sessão SIP estabelecida.", "SUCCESS")
                    _status(f"📞 Chamada Ativa ➔ {destination} ({setup_time}s)")

                    # Envia ACK final
                    ack_branch_final = f"z9hG4bK-{uuid.uuid4().hex[:8]}"
                    to_field_final = f"<sip:{destination}@{domain}>" + (f";tag={peer_to_tag}" if peer_to_tag else "")
                    ack_final = (
                        f"ACK sip:{destination}@{domain} SIP/2.0\r\n"
                        f"Via: SIP/2.0/{'TCP' if is_tcp else 'UDP'} {my_ip}:{my_port};branch={ack_branch_final};rport\r\n"
                        f"Max-Forwards: 70\r\n"
                        f"From: \"{ramal}\" <sip:{ramal}@{domain}>;tag={from_tag}\r\n"
                        f"To: {to_field_final}\r\n"
                        f"Call-ID: {call_id}\r\n"
                        f"CSeq: {current_cseq} ACK\r\n"
                        f"Content-Length: 0\r\n\r\n"
                    )
                    if is_tcp:
                        sock.sendall(ack_final.encode("utf-8"))
                    else:
                        sock.sendto(ack_final.encode("utf-8"), (host, port))

                    # Extrai o endereço de mídia SDP retornado pelo Asterisk
                    last_resp = resp_data
                    remote_rtp_ip, remote_rtp_port = cls.parse_sdp_media(last_resp, host)
                    rtp_packets = cls.extract_pcap_rtp_packets(pcap_file)

                    if remote_rtp_port > 0 and rtp_packets:
                        _log(f"🎵 Transmitindo áudio G.711a do PCAP para {remote_rtp_ip}:{remote_rtp_port} ({len(rtp_packets)} pacotes RTP em loop)...", "INFO")
                    else:
                        _log(f"⏱️ Mantendo canal aberto por até {duration_sec:.0f}s (ou até clique em Encerrar)...", "INFO")

                    active_start = time.time()
                    rtp_sock = None
                    if remote_rtp_port > 0 and rtp_packets:
                        try:
                            rtp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            if local_ip:
                                try:
                                    rtp_sock.bind((local_ip, media_port))
                                except Exception:
                                    pass
                        except Exception:
                            rtp_sock = None

                    pkt_idx = 0
                    seq_num = 1
                    timestamp = 0
                    next_pkt_time = time.time()

                    try:
                        while time.time() - active_start < duration_sec:
                            if stop_event and stop_event.is_set():
                                _log("⏹️ Encerrando chamada por solicitação do usuário...", "INFO")
                                break

                            if rtp_sock and rtp_packets and remote_rtp_port > 0:
                                raw_pkt = rtp_packets[pkt_idx % len(rtp_packets)]
                                pkt_idx += 1

                                # Atualiza cabeçalho RTP (SeqNum e Timestamp para áudio contínuo e suave)
                                if len(raw_pkt) >= 12:
                                    seq_b = struct.pack(">H", seq_num & 0xFFFF)
                                    ts_b = struct.pack(">I", timestamp & 0xFFFFFFFF)
                                    mod_pkt = raw_pkt[:2] + seq_b + ts_b + raw_pkt[8:]
                                else:
                                    mod_pkt = raw_pkt

                                try:
                                    rtp_sock.sendto(mod_pkt, (remote_rtp_ip, remote_rtp_port))
                                except Exception:
                                    pass

                                seq_num += 1
                                timestamp += 160  # 20ms de áudio G.711a @ 8000Hz

                                next_pkt_time += 0.020
                                sleep_time = next_pkt_time - time.time()
                                if sleep_time > 0:
                                    time.sleep(sleep_time)
                                elif sleep_time < -0.1:
                                    next_pkt_time = time.time()
                            else:
                                time.sleep(0.05)
                    finally:
                        if rtp_sock:
                            try:
                                rtp_sock.close()
                            except Exception:
                                pass

                    # Envia BYE para desligar a chamada
                    bye_branch = f"z9hG4bK-{uuid.uuid4().hex[:8]}"
                    bye_msg = (
                        f"BYE sip:{destination}@{domain} SIP/2.0\r\n"
                        f"Via: SIP/2.0/{'TCP' if is_tcp else 'UDP'} {my_ip}:{my_port};branch={bye_branch};rport\r\n"
                        f"Max-Forwards: 70\r\n"
                        f"From: \"{ramal}\" <sip:{ramal}@{domain}>;tag={from_tag}\r\n"
                        f"To: {to_field_final}\r\n"
                        f"Call-ID: {call_id}\r\n"
                        f"CSeq: {current_cseq + 1} BYE\r\n"
                        f"User-Agent: SIPp-Load-Tester-Pro\r\n"
                        f"Content-Length: 0\r\n\r\n"
                    )
                    if is_tcp:
                        sock.sendall(bye_msg.encode("utf-8"))
                    else:
                        sock.sendto(bye_msg.encode("utf-8"), (host, port))

                    _log(f"➔ BYE enviado para {destination}@{domain}. Aguardando confirmação...", "INFO")
                    
                    try:
                        sock.settimeout(2.0)
                        if is_tcp:
                            sock.recv(4096)
                        else:
                            sock.recvfrom(4096)
                        _log("◄ 200 OK recebido ao BYE. Sessão encerrada com êxito.", "SUCCESS")
                    except Exception:
                        _log("Sessão finalizada.", "INFO")

                    total_dur = round(time.time() - start_time, 2)
                    _status("Chamada Finalizada com Sucesso")
                    return True, 200, f"Chamada concluída com sucesso (Duração total: {total_dur}s)"

                # Se erro do PBX (ex: 403, 404, 486, 503)
                if code >= 400:
                    # Envia ACK para fechar a transação
                    ack_branch_err = f"z9hG4bK-{uuid.uuid4().hex[:8]}"
                    to_field_err = f"<sip:{destination}@{domain}>" + (f";tag={peer_to_tag}" if peer_to_tag else "")
                    ack_err = (
                        f"ACK sip:{destination}@{domain} SIP/2.0\r\n"
                        f"Via: SIP/2.0/{'TCP' if is_tcp else 'UDP'} {my_ip}:{my_port};branch={ack_branch_err};rport\r\n"
                        f"Max-Forwards: 70\r\n"
                        f"From: \"{ramal}\" <sip:{ramal}@{domain}>;tag={from_tag}\r\n"
                        f"To: {to_field_err}\r\n"
                        f"Call-ID: {call_id}\r\n"
                        f"CSeq: {current_cseq} ACK\r\n"
                        f"Content-Length: 0\r\n\r\n"
                    )
                    try:
                        if is_tcp:
                            sock.sendall(ack_err.encode("utf-8"))
                        else:
                            sock.sendto(ack_err.encode("utf-8"), (host, port))
                    except Exception:
                        pass

                    _log(f"❌ PBX recusou a chamada: SIP {code} {reason}", "ERROR")
                    _status(f"Falha: SIP {code} {reason}")
                    return False, code, f"PBX recusou com {code} ({reason})"

        except Exception as e:
            _log(f"❌ Erro na chamada única: {e}", "ERROR")
            _status(f"Erro: {e}")
            return False, 0, str(e)
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
