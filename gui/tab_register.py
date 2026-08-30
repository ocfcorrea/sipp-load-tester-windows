"""
Tab Register - Aba 1: Conexão SIP, Portas Locais/Mídia, Registro com LED e Chamada Única.
Estilo Shadcn Luna Minimalista com cores neutras e campos organizados.
"""

from tkinter import filedialog, messagebox
import customtkinter as ctk

from core.config_manager import ConfigManager
from core.sipp_engine import SippEngine
from core.sipp_downloader import SippLocator
from gui.components.led_indicator import LedIndicator


class TabRegister(ctk.CTkScrollableFrame):
    """Aba para configuração do ramal, portas locais/mídia, teste de registro com LED e chamada única."""

    def __init__(self, master, config_mgr: ConfigManager, sipp_engine: SippEngine, log_callback, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.config_mgr = config_mgr
        self.sipp_engine = sipp_engine
        self.log_callback = log_callback

        self._show_password = False

        self._build_ui()
        self.load_from_config()

    def _build_ui(self):
        self.grid_columnconfigure((0, 1), weight=1)

        # -------------------------------------------------------------
        # CARD 1: CONFIGURAÇÃO DE CONEXÃO & IDENTIDADE SIP
        # -------------------------------------------------------------
        conn_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        conn_card.pack(fill="x", padx=10, pady=8)

        lbl_conn_title = ctk.CTkLabel(
            conn_card,
            text="📡 Parâmetros de Conexão & Identidade SIP",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f4f4f5"
        )
        lbl_conn_title.pack(anchor="w", padx=16, pady=(14, 6))

        grid_frame = ctk.CTkFrame(conn_card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=16, pady=6)
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        # 1. Asterisk IP
        f_ip = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f_ip.grid(row=0, column=0, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(f_ip, text="Alvo Asterisk IP / FQDN*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_asterisk_ip = ctk.CTkEntry(f_ip, placeholder_text="Ex: 192.168.68.205", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_asterisk_ip.pack(fill="x", pady=(2, 0))

        # 2. Asterisk Port & Transport
        f_port_transp = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f_port_transp.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        f_port_transp.grid_columnconfigure(0, weight=1)
        f_port_transp.grid_columnconfigure(1, weight=1)

        f_port = ctk.CTkFrame(f_port_transp, fg_color="transparent")
        f_port.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkLabel(f_port, text="Porta SIP*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_asterisk_port = ctk.CTkEntry(f_port, placeholder_text="5060", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_asterisk_port.pack(fill="x", pady=(2, 0))

        f_transp = ctk.CTkFrame(f_port_transp, fg_color="transparent")
        f_transp.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        ctk.CTkLabel(f_transp, text="Transporte*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.combo_transport = ctk.CTkComboBox(f_transp, values=["u1 (UDP)", "t1 (TCP)"], fg_color="#09090b", border_color="#27272a", button_color="#27272a", text_color="#f4f4f5")
        self.combo_transport.pack(fill="x", pady=(2, 0))

        # 3. SIP Domain
        f_domain = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f_domain.grid(row=1, column=0, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(f_domain, text="Domínio SIP (Identidade)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_sip_domain = ctk.CTkEntry(f_domain, placeholder_text="Ex: 192.168.68.205 ou sip.empresa.com", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_sip_domain.pack(fill="x", pady=(2, 0))

        # 4. IP Local (Interface)
        f_local_ip = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f_local_ip.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(f_local_ip, text="IP Local (Interface) [Opcional]", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_local_ip = ctk.CTkEntry(f_local_ip, placeholder_text="Vazio = autodetectar", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_local_ip.pack(fill="x", pady=(2, 0))

        # 5. RAMAL e USUÁRIO DE AUTENTICAÇÃO
        f_ramal = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f_ramal.grid(row=2, column=0, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(f_ramal, text="Ramal (Identidade / Caller ID)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_ramal = ctk.CTkEntry(f_ramal, placeholder_text="Ex: 1002 ou 108$1002", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_ramal.pack(fill="x", pady=(2, 0))

        f_auth_user = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f_auth_user.grid(row=2, column=1, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(f_auth_user, text="Usuário de Autenticação (Auth User)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_usuario_auth = ctk.CTkEntry(f_auth_user, placeholder_text="Usuário Digest (ex: 108$1002 ou 1002)", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_usuario_auth.pack(fill="x", pady=(2, 0))

        # 6. Senha
        f_senha = ctk.CTkFrame(grid_frame, fg_color="transparent")
        f_senha.grid(row=3, column=0, columnspan=2, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(f_senha, text="Senha do Ramal*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        
        pass_sub = ctk.CTkFrame(f_senha, fg_color="transparent")
        pass_sub.pack(fill="x", pady=(2, 0))
        self.entry_senha = ctk.CTkEntry(pass_sub, show="•", placeholder_text="Senha do ramal", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_senha.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.btn_toggle_pass = ctk.CTkButton(
            pass_sub,
            text="👁",
            width=36,
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self._toggle_password
        )
        self.btn_toggle_pass.pack(side="right")

        # 7. Executável SIPp
        f_sipp = ctk.CTkFrame(conn_card, fg_color="transparent")
        f_sipp.pack(fill="x", padx=22, pady=(6, 14))
        ctk.CTkLabel(f_sipp, text="Caminho do Executável SIPp*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        
        sipp_sub = ctk.CTkFrame(f_sipp, fg_color="transparent")
        sipp_sub.pack(fill="x", pady=(2, 0))
        self.entry_sipp_path = ctk.CTkEntry(sipp_sub, placeholder_text="bin/sipp/sipp.exe", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_sipp_path.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_browse = ctk.CTkButton(
            sipp_sub,
            text="Procurar...",
            width=90,
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self._browse_sipp
        )
        btn_browse.pack(side="left", padx=2)

        btn_detect = ctk.CTkButton(
            sipp_sub,
            text="Verificar SIPp",
            width=100,
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self._check_sipp
        )
        btn_detect.pack(side="left", padx=2)

        # -------------------------------------------------------------
        # CARD 2: PORTAS LOCAIS, RANGE DE MÍDIA RTP & ÁUDIO PCAP
        # -------------------------------------------------------------
        net_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        net_card.pack(fill="x", padx=10, pady=8)

        lbl_net_title = ctk.CTkLabel(
            net_card,
            text="🌐 Portas Locais & Range de Mídia RTP / Áudio PCAP",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f4f4f5"
        )
        lbl_net_title.pack(anchor="w", padx=16, pady=(14, 6))

        grid_net = ctk.CTkFrame(net_card, fg_color="transparent")
        grid_net.pack(fill="x", padx=16, pady=6)
        grid_net.grid_columnconfigure((0, 1), weight=1)

        # Porta Local SIP (-p)
        f_lp = ctk.CTkFrame(grid_net, fg_color="transparent")
        f_lp.grid(row=0, column=0, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(f_lp, text="Porta Local SIP (-p) [Vazio = Automático]", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_local_port = ctk.CTkEntry(f_lp, placeholder_text="Ex: 5060 ou vazio", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_local_port.pack(fill="x", pady=(2, 0))

        # Porta Base Mídia RTP (-mp)
        f_mp = ctk.CTkFrame(grid_net, fg_color="transparent")
        f_mp.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(f_mp, text="Porta Base Mídia RTP (-mp)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_media_port = ctk.CTkEntry(f_mp, placeholder_text="Ex: 6000 ou 10000", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_media_port.pack(fill="x", pady=(2, 0))

        # Arquivo de Áudio PCAP
        f_pcap = ctk.CTkFrame(net_card, fg_color="transparent")
        f_pcap.pack(fill="x", padx=22, pady=(4, 14))
        ctk.CTkLabel(f_pcap, text="Arquivo de Áudio PCAP (play_pcap_audio)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")

        pcap_sub = ctk.CTkFrame(f_pcap, fg_color="transparent")
        pcap_sub.pack(fill="x", pady=(2, 0))
        self.entry_pcap_file = ctk.CTkEntry(pcap_sub, placeholder_text="pcap/g711a.pcap", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_pcap_file.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_browse_pcap = ctk.CTkButton(
            pcap_sub,
            text="Procurar PCAP...",
            width=110,
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self._browse_pcap
        )
        btn_browse_pcap.pack(side="left")

        # -------------------------------------------------------------
        # CARD 3: TESTE DE REGISTRO COM LED DE STATUS
        # -------------------------------------------------------------
        reg_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        reg_card.pack(fill="x", padx=10, pady=8)

        lbl_reg_title = ctk.CTkLabel(
            reg_card,
            text="🔐 Autenticação & Teste de Registro SIP",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f4f4f5"
        )
        lbl_reg_title.pack(anchor="w", padx=16, pady=(14, 6))

        reg_content = ctk.CTkFrame(reg_card, fg_color="transparent")
        reg_content.pack(fill="x", padx=16, pady=(4, 14))

        # LED Indicador
        self.led_indicator = LedIndicator(reg_content, label_text="Status do Registro SIP")
        self.led_indicator.pack(side="left", fill="x", expand=True, padx=6)

        # Botão Testar Registro
        self.btn_test_register = ctk.CTkButton(
            reg_content,
            text="⚡ Testar Registro do Ramal",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27272a",
            hover_color="#14532d",
            text_color="#4ade80",
            border_width=1,
            border_color="#166534",
            height=34,
            width=190,
            command=self._on_test_register
        )
        self.btn_test_register.pack(side="right", padx=6)

        # -------------------------------------------------------------
        # CARD 4: CHAMADA ÚNICA DE TESTE (LIGAR & DESLIGAR)
        # -------------------------------------------------------------
        single_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        single_card.pack(fill="x", padx=10, pady=8)

        lbl_single_title = ctk.CTkLabel(
            single_card,
            text="📞 Teste de Chamada Única (Rápida)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f4f4f5"
        )
        lbl_single_title.pack(anchor="w", padx=16, pady=(14, 6))

        single_content = ctk.CTkFrame(single_card, fg_color="transparent")
        single_content.pack(fill="x", padx=16, pady=(4, 10))
        single_content.grid_columnconfigure(0, weight=2)
        single_content.grid_columnconfigure(1, weight=1)
        single_content.grid_columnconfigure(2, weight=1)

        f_dest = ctk.CTkFrame(single_content, fg_color="transparent")
        f_dest.grid(row=0, column=0, sticky="ew", padx=6)
        ctk.CTkLabel(f_dest, text="Destino para Teste Único", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_single_dest = ctk.CTkEntry(f_dest, placeholder_text="Ex: 22221864 ou 9999", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_single_dest.pack(fill="x", pady=(2, 0))

        self.btn_start_single = ctk.CTkButton(
            single_content,
            text="▶️ Ligar",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27272a",
            hover_color="#1e3a8a",
            text_color="#60a5fa",
            border_width=1,
            border_color="#1e40af",
            height=32,
            command=self._on_start_single_call
        )
        self.btn_start_single.grid(row=0, column=1, sticky="ew", padx=6, pady=(18, 0))

        self.btn_stop_single = ctk.CTkButton(
            single_content,
            text="⏹️ Desligar",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27272a",
            hover_color="#3f1414",
            text_color="#f87171",
            border_width=1,
            border_color="#7f1d1d",
            height=32,
            command=self._on_stop_single_call
        )
        self.btn_stop_single.grid(row=0, column=2, sticky="ew", padx=6, pady=(18, 0))

        # Status da Chamada Única
        self.lbl_single_status = ctk.CTkLabel(
            single_card,
            text="Pronto para testar",
            font=ctk.CTkFont(size=11),
            text_color="#71717a"
        )
        self.lbl_single_status.pack(anchor="w", padx=22, pady=(0, 10))

        # -------------------------------------------------------------
        # BOTÕES DE AÇÃO: SALVAR CONFIGURAÇÕES
        # -------------------------------------------------------------
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=8)

        self.btn_save_config = ctk.CTkButton(
            action_bar,
            text="💾 Salvar Configurações de Conexão",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#fafafa",
            hover_color="#e4e4e7",
            text_color="#18181b",
            height=36,
            command=self.save_to_config
        )
        self.btn_save_config.pack(side="right", padx=6)

    def _toggle_password(self):
        self._show_password = not self._show_password
        self.entry_senha.configure(show="" if self._show_password else "•")
        self.btn_toggle_pass.configure(text="🔒" if self._show_password else "👁")

    def _browse_sipp(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o executável do SIPp",
            filetypes=[("Executáveis", "*.exe;sipp"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.entry_sipp_path.delete(0, "end")
            self.entry_sipp_path.insert(0, file_path)

    def _browse_pcap(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo de áudio PCAP",
            filetypes=[("Arquivos PCAP", "*.pcap"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.entry_pcap_file.delete(0, "end")
            self.entry_pcap_file.insert(0, file_path)

    def _check_sipp(self):
        path = self.entry_sipp_path.get().strip()
        binary = SippLocator.find_sipp(path)
        if not binary:
            messagebox.showerror("Erro SIPp", f"SIPp não foi localizado em '{path}'.\n\nPor favor, verifique o caminho.")
            return

        ok, info = SippLocator.check_sipp_version(binary)
        if ok:
            messagebox.showinfo("SIPp Validado", f"Executável SIPp pronto para uso!\n\nCaminho: {binary}\n\n{info}")
        else:
            messagebox.showwarning("Aviso SIPp", f"Executável respondeu com aviso:\n{info}")

    def _on_test_register(self):
        if not self.save_to_config():
            return

        self.led_indicator.set_state("yellow", "Enviando REGISTER...")
        self.btn_test_register.configure(state="disabled")

        def _on_result(success: bool, message: str, duration: float = None):
            self.after(0, lambda: self._handle_register_result(success, message, duration))

        cfg = self.config_mgr.config
        self.sipp_engine.test_registration(
            config=cfg,
            log_callback=self.log_callback,
            result_callback=_on_result
        )

    def _handle_register_result(self, success: bool, message: str, duration: float = None):
        self.btn_test_register.configure(state="normal")
        if success:
            dur_txt = f" ({duration}s)" if duration else ""
            self.led_indicator.set_state("green", f"200 OK — Registrado com Sucesso{dur_txt}")
        else:
            self.led_indicator.set_state("red", f"Falha: {message}")

    def _on_start_single_call(self):
        if not self.save_to_config():
            return

        dest = self.entry_single_dest.get().strip()
        if not dest:
            messagebox.showwarning("Destino Vazio", "Informe um número de destino para a chamada única.")
            return

        self.btn_start_single.configure(state="disabled")
        self.btn_stop_single.configure(state="normal")

        def _on_status(msg: str):
            self.after(0, lambda: self.lbl_single_status.configure(text=msg))
            if "Finalizada" in msg or "Inválido" in msg:
                self.after(0, lambda: self.btn_start_single.configure(state="normal"))

        cfg = self.config_mgr.config
        self.sipp_engine.start_single_call(
            config=cfg,
            destination=dest,
            log_callback=self.log_callback,
            status_callback=_on_status
        )

    def _on_stop_single_call(self):
        self.sipp_engine.stop_single_call()
        self.lbl_single_status.configure(text="Encerrando chamada...")
        self.btn_start_single.configure(state="normal")

    def load_from_config(self):
        cfg = self.config_mgr.config

        self.entry_asterisk_ip.delete(0, "end")
        self.entry_asterisk_ip.insert(0, cfg.get("asterisk_ip", "192.168.68.205"))

        self.entry_asterisk_port.delete(0, "end")
        self.entry_asterisk_port.insert(0, str(cfg.get("asterisk_port", "5060")))

        transp = cfg.get("transport", "u1")
        self.combo_transport.set("t1 (TCP)" if transp == "t1" else "u1 (UDP)")

        self.entry_sip_domain.delete(0, "end")
        self.entry_sip_domain.insert(0, cfg.get("sip_domain", cfg.get("asterisk_ip", "192.168.68.205")))

        self.entry_local_ip.delete(0, "end")
        self.entry_local_ip.insert(0, cfg.get("local_ip", ""))

        self.entry_local_port.delete(0, "end")
        self.entry_local_port.insert(0, str(cfg.get("local_port", "")))

        self.entry_media_port.delete(0, "end")
        self.entry_media_port.insert(0, str(cfg.get("media_port", "6000")))

        self.entry_pcap_file.delete(0, "end")
        self.entry_pcap_file.insert(0, cfg.get("pcap_file", "pcap/g711a.pcap"))

        self.entry_ramal.delete(0, "end")
        self.entry_ramal.insert(0, cfg.get("ramal", "108$1002"))

        self.entry_usuario_auth.delete(0, "end")
        self.entry_usuario_auth.insert(0, cfg.get("usuario_auth", cfg.get("ramal", "108$1002")))

        self.entry_senha.delete(0, "end")
        self.entry_senha.insert(0, cfg.get("senha", ""))

        self.entry_sipp_path.delete(0, "end")
        self.entry_sipp_path.insert(0, cfg.get("sipp_path", "bin/sipp/sipp.exe"))

        self.entry_single_dest.delete(0, "end")
        self.entry_single_dest.insert(0, cfg.get("single_call_dest", "22221864"))

    def save_to_config(self) -> bool:
        ip = self.entry_asterisk_ip.get().strip()
        port = self.entry_asterisk_port.get().strip()
        ramal = self.entry_ramal.get().strip()
        auth_user = self.entry_usuario_auth.get().strip() or ramal
        senha = self.entry_senha.get()

        if not ip:
            messagebox.showerror("Campo Obrigatório", "O IP do Asterisk é obrigatório.")
            return False
        if not port:
            messagebox.showerror("Campo Obrigatório", "A Porta do Asterisk é obrigatória.")
            return False
        if not ramal:
            messagebox.showerror("Campo Obrigatório", "O Ramal é obrigatório.")
            return False

        transp_val = "t1" if "TCP" in self.combo_transport.get() else "u1"

        self.config_mgr.set("asterisk_ip", ip)
        self.config_mgr.set("asterisk_port", port)
        self.config_mgr.set("transport", transp_val)
        self.config_mgr.set("sip_domain", self.entry_sip_domain.get().strip() or ip)
        self.config_mgr.set("local_ip", self.entry_local_ip.get().strip())
        self.config_mgr.set("local_port", self.entry_local_port.get().strip())
        self.config_mgr.set("media_port", self.entry_media_port.get().strip() or "6000")
        self.config_mgr.set("pcap_file", self.entry_pcap_file.get().strip() or "pcap/g711a.pcap")
        self.config_mgr.set("ramal", ramal)
        self.config_mgr.set("usuario_auth", auth_user)
        self.config_mgr.set("senha", senha)
        self.config_mgr.set("sipp_path", self.entry_sipp_path.get().strip() or "bin/sipp/sipp.exe")
        self.config_mgr.set("single_call_dest", self.entry_single_dest.get().strip())

        self.config_mgr.save_config()
        return True
