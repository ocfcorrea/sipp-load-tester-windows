"""
Tab About - Aba 4: Sobre a Aplicação, Topologia de Rede, Fluxos SIP e Documentação Completa.
Estilo Slate / Dark Navy Suave com diagramas e guias técnicos integrados.
"""

import webbrowser
import customtkinter as ctk
from core.version import get_version_tag, get_version_info


class TabAbout(ctk.CTkScrollableFrame):
    """Aba de documentação, topologia e informações detalhadas do sistema."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._build_ui()

    def _build_ui(self):
        ver_info = get_version_info()

        # -------------------------------------------------------------
        # 1. CARD: VISÃO GERAL & INFORMAÇÕES TÉCNICAS
        # -------------------------------------------------------------
        overview_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#272a37", border_width=1, border_color="#383c4e")
        overview_card.pack(fill="x", padx=10, pady=8)

        lbl_ov_title = ctk.CTkLabel(
            overview_card,
            text=f"⚡ SIPp Load Tester Pro — Release {ver_info.get('release_tag', 'v2.0')} Pro",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#f1f5f9"
        )
        lbl_ov_title.pack(anchor="w", padx=16, pady=(14, 4))

        lbl_ov_desc = ctk.CTkLabel(
            overview_card,
            text=(
                "Plataforma avançada de engenharia para testes de carga, estresse e simulação de simultaneidade SIP contra "
                "servidores Asterisk, PBX IP e gateways de telecomunicações. Suporta sinalização com autenticação Digest (401/407), "
                "transmissão real de áudio RTP (PCAP G.711 a-law), estratégias ponderadas de discagem e simulação randômica humana."
            ),
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
            justify="left",
            wraplength=920
        )
        lbl_ov_desc.pack(anchor="w", padx=16, pady=(0, 12))

        # Badges técnicos
        badges_frame = ctk.CTkFrame(overview_card, fg_color="transparent")
        badges_frame.pack(fill="x", padx=16, pady=(0, 12))

        tech_info = [
            ("Versão", f"{ver_info.get('release_tag', 'v2.0')} Pro"),
            ("Commit", f"{ver_info.get('commit', 'HEAD')}"),
            ("Motor SIP", "SIPp v3.2 Win / SipClient"),
            ("Autenticação", "Digest MD5 (RFC 2617)"),
            ("Áudio RTP", "PCMA G.711a (8kHz)"),
            ("Segurança", "Zero Leaks (.env)"),
        ]

        for i, (k, v) in enumerate(tech_info):
            f_b = ctk.CTkFrame(badges_frame, fg_color="#1a1c26", corner_radius=6, border_width=1, border_color="#383c4e")
            f_b.pack(side="left", padx=(0, 8), pady=2)
            ctk.CTkLabel(f_b, text=f"{k}: ", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8").pack(side="left", padx=(8, 2), pady=4)
            ctk.CTkLabel(f_b, text=v, font=ctk.CTkFont(size=11), text_color="#38bdf8" if k in ("Versão", "Commit") else "#f1f5f9").pack(side="left", padx=(0, 8), pady=4)

        # Botões de links rápidos (GitHub Releases e Repositório)
        links_frame = ctk.CTkFrame(overview_card, fg_color="transparent")
        links_frame.pack(fill="x", padx=16, pady=(0, 14))

        btn_rel = ctk.CTkButton(
            links_frame,
            text="📦 Ver Releases & Downloads (.EXE)",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            height=30,
            command=lambda: webbrowser.open("https://github.com/ocfcorrea/TestSIPpWindows/releases")
        )
        btn_rel.pack(side="left", padx=(0, 10))

        btn_repo = ctk.CTkButton(
            links_frame,
            text="⭐ Repositório no GitHub",
            font=ctk.CTkFont(size=12),
            fg_color="#334155",
            hover_color="#475569",
            height=30,
            command=lambda: webbrowser.open("https://github.com/ocfcorrea/TestSIPpWindows")
        )
        btn_repo.pack(side="left", padx=(0, 10))

        # -------------------------------------------------------------
        # 2. CARD: TOPOLOGIA DE REDE & ARQUITETURA DE COMUNICAÇÃO
        # -------------------------------------------------------------
        topo_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#272a37", border_width=1, border_color="#383c4e")
        topo_card.pack(fill="x", padx=10, pady=8)

        lbl_topo_title = ctk.CTkLabel(
            topo_card,
            text="🌐 Topologia de Rede & Fluxo de Comunicação",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f1f5f9"
        )
        lbl_topo_title.pack(anchor="w", padx=16, pady=(14, 6))

        diagram_text = (
            "┌─────────────────────────────────────────┐                ┌─────────────────────────────────────────┐\n"
            "│          CLIENTE GERADOR DE CARGA       │                │          SERVIDOR PBX IP / ASTERISK     │\n"
            "│        (SIPp Load Tester Pro GUI)       │                │                                         │\n"
            "│                                         │                │                                         │\n"
            "│  ┌───────────────────────────────────┐  │                │  ┌───────────────────────────────────┐  │\n"
            "│  │ Core Engine & SipClient (Python)  │  │                │  │ PJSIP / SIP Core Engine           │  │\n"
            "│  │ - Config & Strategy Manager       │  │                │  │ - Endpoint Registry (AOR)         │  │\n"
            "│  │ - Security & Masking Layer        │  │                │  │ - Digest Authentication (401/407) │  │\n"
            "│  └─────────────────┬─────────────────┘  │                │  └─────────────────▲─────────────────┘  │\n"
            "│                    │                    │                │                    │                    │\n"
            "│  ┌─────────────────▼─────────────────┐  │  SIP (UDP/TCP) │  ┌─────────────────┴─────────────────┐  │\n"
            "│  │ SIPp Process (bin/sipp/sipp.exe)  ├─┼────────────────┼─►│ Porta SIP 5060                    │  │\n"
            "│  │ - REGISTER & INVITE Scenarios     │  │  Sinalização   │  │ (From, To, Contact, CSeq, Auth)   │  │\n"
            "│  └─────────────────┬─────────────────┘  │                │  └─────────────────┬─────────────────┘  │\n"
            "│                    │                    │                │                    │                    │\n"
            "│  ┌─────────────────▼─────────────────┐  │   Mídia RTP    │  ┌─────────────────▼─────────────────┐  │\n"
            "│  │ PCAP RTP Player (pcap/g711a.pcap) ├─┼────────────────┼─►│ RTP Engine (Portas 10000-20000)   │  │\n"
            "│  │ - G.711 a-law Audio Stream (8kHz) │  │ (Payload PCMA) │  │ - Echo() / URA / Fila Atendimento │  │\n"
            "│  └───────────────────────────────────┘  │                │  └───────────────────────────────────┘  │\n"
            "└─────────────────────────────────────────┘                └─────────────────────────────────────────┘"
        )

        topo_box = ctk.CTkTextbox(
            topo_card,
            font=ctk.CTkFont(family="Consolas", size=10),
            height=260,
            fg_color="#1a1c26",
            text_color="#38bdf8",
            border_width=1,
            border_color="#383c4e"
        )
        topo_box.pack(fill="x", padx=16, pady=(4, 14))
        topo_box.insert("1.0", diagram_text)
        topo_box.configure(state="disabled")

        # -------------------------------------------------------------
        # 3. CARD: FLUXO DE SINALIZAÇÃO SIP DETALHADO
        # -------------------------------------------------------------
        flow_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#272a37", border_width=1, border_color="#383c4e")
        flow_card.pack(fill="x", padx=10, pady=8)

        lbl_flow_title = ctk.CTkLabel(
            flow_card,
            text="🔄 Diagrama de Sequência SIP (Registro e Chamadas)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f1f5f9"
        )
        lbl_flow_title.pack(anchor="w", padx=16, pady=(14, 6))

        flow_text = (
            "1. FLUXO DE REGISTRO DO RAMAL (SipClient / RFC 3261):\n"
            "   SIPp (UAC)                                         Asterisk (UAS)\n"
            "      | ──────────────── REGISTER (sem auth) ──────────────► | (CSeq: 1 REGISTER)\n"
            "      | ◄─────────────── 401 Unauthorized (Digest) ────────── | (Desafio de autenticação nonce/realm)\n"
            "      | ──────────────── REGISTER (com Digest Auth) ────────► | (CSeq: 2 REGISTER com Authorization)\n"
            "      | ◄─────────────── 200 OK (Expires: 3600s) ──────────── | (Binding do contato ativo! [LED Verde])\n\n"
            "2. FLUXO DE CHAMADA COM ÁUDIO RTP (call.xml):\n"
            "   SIPp (UAC)                                         Asterisk (UAS)\n"
            "      | ──────────────── INVITE (sem auth) ────────────────► | (CSeq: 1 INVITE)\n"
            "      | ◄─────────────── 401 / 407 Proxy Auth Req ────────── | (Desafio Digest)\n"
            "      | ──────────────── ACK ──────────────────────────────► | (Confirmação do desafio)\n"
            "      | ──────────────── INVITE (com Digest + SDP PCMA) ────► | (CSeq: 2 INVITE)\n"
            "      | ◄─────────────── 100 Trying / 180 Ringing ────────── | (Processando / Chamando)\n"
            "      | ◄─────────────── 200 OK (SDP Answer) ──────────────── | (Chamada Atendida)\n"
            "      | ──────────────── ACK ──────────────────────────────► | (Sessão Estabelecida)\n"
            "      | ════════════════ Mídia RTP G.711a (~7s) ════════════► | (Transmissão de Pacotes de Voz)\n"
            "      | ................ Pausa Ponderada Uniforme .......... | (Mantém canal aberto pelo tempo sorteado)\n"
            "      | ──────────────── BYE ──────────────────────────────► | (Desconexão da chamada)\n"
            "      | ◄─────────────── 200 OK ───────────────────────────── | (Chamada encerrada com sucesso)"
        )

        flow_box = ctk.CTkTextbox(
            flow_card,
            font=ctk.CTkFont(family="Consolas", size=10),
            height=300,
            fg_color="#1a1c26",
            text_color="#4ade80",
            border_width=1,
            border_color="#383c4e"
        )
        flow_box.pack(fill="x", padx=16, pady=(4, 14))
        flow_box.insert("1.0", flow_text)
        flow_box.configure(state="disabled")

        # -------------------------------------------------------------
        # 4. CARD: GUIA DE ESTRATÉGIA, SIMULTANEIDADE & MODO HUMANO
        # -------------------------------------------------------------
        strat_guide_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#272a37", border_width=1, border_color="#383c4e")
        strat_guide_card.pack(fill="x", padx=10, pady=8)

        lbl_sg_title = ctk.CTkLabel(
            strat_guide_card,
            text="🎯 Guia de Estratégias de Discagem & Modo Randômico",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f1f5f9"
        )
        lbl_sg_title.pack(anchor="w", padx=16, pady=(14, 6))

        sg_text = (
            "• Simultaneidade em Regime Constante (-l):\n"
            "  O parâmetro -l do SIPp define um patamar que ele mantém ativo continuamente. Sempre que uma chamada é encerrada,\n"
            "  o motor cria outra imediatamente para repor a vaga. Se Total = 0 (-m omitido), o teste roda indefinidamente.\n\n"
            "• Taxa de Reposição (-r e -rp):\n"
            "  Controla a velocidade máxima em que novas chamadas são geradas. Mantenha a taxa folgada (>= metade de simultâneas por segundo)\n"
            "  para que o patamar de chamadas simultâneas não afunde quando várias chamadas encerrarem juntas.\n\n"
            "• Simulação Humana / Tráfego Orgânico:\n"
            "  Simula um callcenter ou tráfego real onde múltiplos usuários discam e desligam independentemente.\n"
            "  - Intervalo Mín/Máx: Define o jitter e dispersão entre tentativas de discagem.\n"
            "  - Chance de Pico (Burst %): Introduz surtos aleatórios simulando momentos de pico.\n"
            "  - Token Dinâmico: Gera identificadores únicos para rastrear origens e sessões.\n\n"
            "• Roteamento Ponderado de Destinos (Weighted Distribution):\n"
            "  Permite definir de 1 até 10 números de destino, cada um com seu peso relativo (1-100).\n"
            "  O motor calcula a proporção percentual exata e gera um pool randômico ponderado no CSV de credenciais."
        )

        sg_box = ctk.CTkTextbox(
            strat_guide_card,
            font=ctk.CTkFont(family="Consolas", size=10),
            height=200,
            fg_color="#1a1c26",
            text_color="#e2e8f0",
            border_width=1,
            border_color="#383c4e"
        )
        sg_box.pack(fill="x", padx=16, pady=(4, 14))
        sg_box.insert("1.0", sg_text)
        sg_box.configure(state="disabled")

        # -------------------------------------------------------------
        # 5. CARD: CUIDADOS NO ASTERISK & DIAGNÓSTICO
        # -------------------------------------------------------------
        ast_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#272a37", border_width=1, border_color="#383c4e")
        ast_card.pack(fill="x", padx=10, pady=8)

        lbl_ast_title = ctk.CTkLabel(
            ast_card,
            text="🛠️ Cuidados no Asterisk & Diagnóstico de Rede",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f1f5f9"
        )
        lbl_ast_title.pack(anchor="w", padx=16, pady=(14, 6))

        ast_text = (
            "1. Limite de Chamadas por Endpoint (pjsip.conf):\n"
            "   Certifique-se de desabilitar o limite por device state no endpoint do ramal de teste:\n"
            "   [1002]\n"
            "   type=endpoint\n"
            "   device_state_busy_at=0        ; 0 = sem limite de chamadas simultâneas\n"
            "   max_contacts=100              ; suporta múltiplos registros se necessário\n"
            "   qualify_frequency=0           ; desabilita qualify OPTIONS durante o teste\n\n"
            "2. Destino com Resposta e Mídia Sustentada (extensions.conf):\n"
            "   O destino configurado deve atender e manter o canal aberto:\n"
            "   exten => 9999,1,Answer()\n"
            "    same => n,Echo()             ; devolve o áudio RTP nos dois sentidos\n"
            "    same => n,Hangup()\n\n"
            "3. Faixa de Portas RTP (rtp.conf):\n"
            "   Para 100 chamadas simultâneas, você precisa de no mínimo 200 portas RTP (ex.: 10000 a 20000).\n\n"
            "4. Diagnóstico em Tempo Real com sngrep ou tcpdump:\n"
            "   - sngrep -d any port 5060\n"
            "   - tcpdump -n -i any port 5060 -vv"
        )

        ast_box = ctk.CTkTextbox(
            ast_card,
            font=ctk.CTkFont(family="Consolas", size=10),
            height=220,
            fg_color="#1a1c26",
            text_color="#e2e8f0",
            border_width=1,
            border_color="#383c4e"
        )
        ast_box.pack(fill="x", padx=16, pady=(4, 14))
        ast_box.insert("1.0", ast_text)
        ast_box.configure(state="disabled")
