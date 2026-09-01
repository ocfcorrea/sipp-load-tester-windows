"""
Main Window - Janela principal da aplicação SIPp Load Tester Pro.
Coordena as 4 abas, navegação, eventos globais e barra de status.
Estilo Slate / Dark Navy Suave com paleta moderna e ergonômica.
"""

from tkinter import messagebox
import customtkinter as ctk

from core.config_manager import ConfigManager
from core.sipp_engine import SippEngine
from core.version import get_app_title, get_version_tag
from gui.tab_register import TabRegister
from gui.tab_strategy import TabStrategy
from gui.tab_console import TabConsole
from gui.tab_about import TabAbout


class MainWindow(ctk.CTk):
    """Janela principal do aplicativo."""

    def __init__(self):
        super().__init__()

        self.title(f"{get_app_title()} — Asterisk / PBX IP")
        self.geometry("1140, 780")
        self.minsize(1020, 680)

        # Configura tema escuro Slate / Dark Navy Suave
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.configure(fg_color="#1e222d")

        # Inicializa motores e configurações
        self.config_mgr = ConfigManager()
        self.sipp_engine = SippEngine()

        self._build_ui()

    def _build_ui(self):
        # -------------------------------------------------------------
        # 1. CABEÇALHO GLOBAL (HEADER) - Slate Style
        # -------------------------------------------------------------
        header = ctk.CTkFrame(self, height=54, corner_radius=0, fg_color="#272a37", border_width=1, border_color="#383c4e")
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Título e Logo
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=16, pady=8)

        lbl_logo = ctk.CTkLabel(title_frame, text="⚡", font=ctk.CTkFont(size=20), text_color="#38bdf8")
        lbl_logo.pack(side="left", padx=(0, 8))

        lbl_app_title = ctk.CTkLabel(
            title_frame,
            text="SIPp Load Tester Pro",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f1f5f9"
        )
        lbl_app_title.pack(side="left")

        lbl_app_sub = ctk.CTkLabel(
            title_frame,
            text=f" {get_version_tag()} — Gerador de Carga & Simultâneas SIP",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        lbl_app_sub.pack(side="left")

        # Botão Global de Emergência no Header
        self.btn_global_kill = ctk.CTkButton(
            header,
            text="🛑 Derrubar Todas as Chamadas",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#383c4e",
            hover_color="#991b1b",
            text_color="#f87171",
            border_width=1,
            border_color="#7f1d1d",
            height=32,
            corner_radius=6,
            command=self.kill_all_calls
        )
        self.btn_global_kill.pack(side="right", padx=16, pady=10)

        # -------------------------------------------------------------
        # 2. SISTEMA DE ABAS (TABVIEW)
        # -------------------------------------------------------------
        self.tabview = ctk.CTkTabview(
            self,
            corner_radius=8,
            fg_color="#1e222d",
            segmented_button_fg_color="#212430",
            segmented_button_selected_color="#0284c7",
            segmented_button_selected_hover_color="#0369a1",
            segmented_button_unselected_hover_color="#333749",
            text_color="#f1f5f9"
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(4, 4))

        # Criação das 4 abas
        self.tab_reg_name = "🔐 1. Registro & Conexão SIP"
        self.tab_strat_name = "🎯 2. Estratégia de Discagem"
        self.tab_cons_name = "🖥️ 3. Console & Métricas ao Vivo"
        self.tab_about_name = "📖 4. Sobre & Topologia"

        self.tabview.add(self.tab_reg_name)
        self.tabview.add(self.tab_strat_name)
        self.tabview.add(self.tab_cons_name)
        self.tabview.add(self.tab_about_name)

        # Instanciação do conteúdo das abas
        self.tab_register = TabRegister(
            self.tabview.tab(self.tab_reg_name),
            config_mgr=self.config_mgr,
            sipp_engine=self.sipp_engine,
            log_callback=self.log_message
        )
        self.tab_register.pack(fill="both", expand=True)

        self.tab_strategy = TabStrategy(
            self.tabview.tab(self.tab_strat_name),
            config_mgr=self.config_mgr
        )
        self.tab_strategy.pack(fill="both", expand=True)

        self.tab_console = TabConsole(
            self.tabview.tab(self.tab_cons_name),
            config_mgr=self.config_mgr,
            sipp_engine=self.sipp_engine,
            start_load_fn=self.start_load_test,
            kill_all_fn=self.kill_all_calls
        )
        self.tab_console.pack(fill="both", expand=True)

        self.tab_about = TabAbout(
            self.tabview.tab(self.tab_about_name)
        )
        self.tab_about.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # 3. BARRA DE STATUS (FOOTER)
        # -------------------------------------------------------------
        footer = ctk.CTkFrame(self, height=24, corner_radius=0, fg_color="#272a37", border_width=1, border_color="#383c4e")
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.lbl_status = ctk.CTkLabel(
            footer,
            text="Pronto | SIPp Load Tester Pro",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        self.lbl_status.pack(side="left", padx=14)

        self.lbl_target_info = ctk.CTkLabel(
            footer,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        self.lbl_target_info.pack(side="right", padx=14)

        self._update_footer_info()

    def _update_footer_info(self):
        cfg = self.config_mgr.config
        ip = cfg.get("asterisk_ip", "")
        port = cfg.get("asterisk_port", 5060)
        ramal = cfg.get("ramal", "")
        if ip and ramal:
            self.lbl_target_info.configure(text=f"Destino: {ip}:{port} | Ramal: {ramal}")
        else:
            self.lbl_target_info.configure(text="Configuração pendente")

    def log_message(self, message: str, level: str = "INFO"):
        """Encaminha mensagem para o console da Aba 3 e atualiza a barra de status."""
        self.tab_console.append_log(message, level)
        if level in ["INFO", "SUCCESS", "ERROR"]:
            clean_msg = message.replace("[REGISTRO] ", "").replace("[TESTE_CARGA] ", "")
            self.lbl_status.configure(text=clean_msg[:70])

    def start_load_test(self):
        """Inicia o teste de carga a partir da Aba 3."""
        # Salva dados das abas 1 e 2
        if not self.tab_register.save_to_config():
            self.tabview.set(self.tab_reg_name)
            return

        if not self.tab_strategy.save_to_config():
            self.tabview.set(self.tab_strat_name)
            return

        self._update_footer_info()
        cfg = self.config_mgr.config

        def _on_finished(rc: int):
            self.tab_console.set_execution_state(False)
            if rc == 0:
                self.log_message("✅ Teste de carga finalizado com êxito.", "SUCCESS")
            else:
                self.log_message(f"🛑 Teste de carga encerrado (código {rc}).", "INFO")

        self.tab_console.set_execution_state(True)
        self.tab_console.reset_metrics(int(cfg.get("simultaneas", 100)))

        # Inicia processo do SIPp
        ok = self.sipp_engine.start_load_test(
            config=cfg,
            log_callback=self.log_message,
            stats_callback=self.tab_console.update_metrics,
            finished_callback=_on_finished
        )
        if not ok:
            self.tab_console.set_execution_state(False)

    def kill_all_calls(self):
        """Derruba todos os testes e processos SIPp ativos."""
        if not self.sipp_engine.is_running and not self.sipp_engine.is_single_call_running:
            messagebox.showinfo("Status", "Nenhum teste de carga ou chamada está ativo no momento.")
            return

        if messagebox.askyesno("Confirmar Parada", "Deseja realmente interromper todas as chamadas e processos SIPp imediatamente?"):
            self.sipp_engine.kill_all()
            self.log_message("[GLOBAL] Todas as chamadas foram encerradas pelo operador.", "WARNING")
            self.lbl_status.configure(text="Chamadas canceladas pelo operador.")
