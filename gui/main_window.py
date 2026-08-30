"""
Main Window - Janela principal da aplicação SIPp Load Tester Pro.
Coordena as 3 abas, navegação, eventos globais e barra de status.
"""

from tkinter import messagebox
import customtkinter as ctk

from core.config_manager import ConfigManager
from core.sipp_engine import SippEngine
from gui.tab_register import TabRegister
from gui.tab_strategy import TabStrategy
from gui.tab_console import TabConsole
from gui.tab_about import TabAbout


class MainWindow(ctk.CTk):
    """Janela principal do aplicativo."""

    def __init__(self):
        super().__init__()

        self.title("SIPp Load Tester Pro — Asterisk / PBX IP")
        self.geometry("1100, 780")
        self.minsize(980, 680)

        # Configura tema escuro moderno
        # Configura tema escuro minimalista Shadcn Luna
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.configure(fg_color="#09090b")

        # Inicializa motores e configurações
        self.config_mgr = ConfigManager()
        self.sipp_engine = SippEngine()

        self._build_ui()

    def _build_ui(self):
        # -------------------------------------------------------------
        # 1. CABEÇALHO GLOBAL (HEADER) - Shadcn Luna style
        # -------------------------------------------------------------
        header = ctk.CTkFrame(self, height=54, corner_radius=0, fg_color="#18181b", border_width=1, border_color="#27272a")
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Título e Logo
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=18, pady=8)

        lbl_logo = ctk.CTkLabel(title_frame, text="⚡", font=ctk.CTkFont(size=20), text_color="#f4f4f5")
        lbl_logo.pack(side="left", padx=(0, 8))

        lbl_app_title = ctk.CTkLabel(
            title_frame,
            text="SIPp Load Tester Pro",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f4f4f5"
        )
        lbl_app_title.pack(side="left")

        lbl_app_sub = ctk.CTkLabel(
            title_frame,
            text=" — Gerador de Carga & Simultâneas SIP",
            font=ctk.CTkFont(size=12),
            text_color="#71717a"
        )
        lbl_app_sub.pack(side="left")

        # Botão Global de Emergência no Header (Estilo Shadcn Destructive Suave)
        self.btn_global_kill = ctk.CTkButton(
            header,
            text="🛑 Derrubar Todas as Chamadas",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27272a",
            hover_color="#3f1414",
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
            fg_color="#121215",
            segmented_button_fg_color="#18181b",
            segmented_button_selected_color="#27272a",
            segmented_button_selected_hover_color="#3f3f46",
            segmented_button_unselected_hover_color="#27272a",
            text_color="#f4f4f5"
        )
        self.tabview.pack(fill="both", expand=True, padx=12, pady=(6, 4))

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
        # 3. BARRA DE STATUS (FOOTER) - Sem nome L5 Networks
        # -------------------------------------------------------------
        footer = ctk.CTkFrame(self, height=24, corner_radius=0, fg_color="#18181b", border_width=1, border_color="#27272a")
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.lbl_status = ctk.CTkLabel(
            footer,
            text="Pronto | SIPp Load Tester Pro",
            font=ctk.CTkFont(size=11),
            text_color="#71717a"
        )
        self.lbl_status.pack(side="left", padx=14)

        self.lbl_target_info = ctk.CTkLabel(
            footer,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#a1a1aa"
        )
        self.lbl_target_info.pack(side="right", padx=14)

        self._update_footer_info()

    def _update_footer_info(self):
        cfg = self.config_mgr.config
        target = f"{cfg.get('asterisk_ip', '')}:{cfg.get('asterisk_port', '5060')}"
        ramal = cfg.get('ramal', '')
        self.lbl_target_info.configure(text=f"Alvo: {target} | Ramal: {ramal}")

    def log_message(self, message: str, level: str = "INFO"):
        """Encaminha mensagem de log para a aba de console na thread correta."""
        self.after(0, lambda: self.tab_console.log(message, level))

    def start_load_test(self):
        """Salva configurações de todas as abas e inicia o teste de carga."""
        self.tab_register.save_to_config()
        ok = self.tab_strategy.save_to_config()
        if not ok:
            return

        cfg = self.config_mgr.config
        self._update_footer_info()

        # Muda para a aba de console
        self.tabview.set(self.tab_cons_name)

        max_sim = int(cfg.get("simultaneas", 100))
        self.tab_console.reset_metrics(max_sim)
        self.tab_console.set_execution_state(True)
        self.lbl_status.configure(text="⚡ Teste de Carga em Execução...")

        def _on_stats(stats: dict):
            self.after(0, lambda: self.tab_console.update_metrics(stats))

        def _on_finished(rc: int):
            self.after(0, lambda: self._on_test_finished(rc))

        started = self.sipp_engine.start_load_test(
            config=cfg,
            log_callback=self.log_message,
            stats_callback=_on_stats,
            finished_callback=_on_finished
        )

        if not started:
            self.tab_console.set_execution_state(False)
            self.lbl_status.configure(text="Pronto (Falha na inicialização)")

    def _on_test_finished(self, return_code: int):
        """Chamado quando o teste termina."""
        self.tab_console.set_execution_state(False)
        self.lbl_status.configure(text=f"Pronto (Teste finalizado com código {return_code})")

    def kill_all_calls(self):
        """Encerra todas as chamadas imediatamente."""
        self.sipp_engine.kill_all()
        self.tab_console.set_execution_state(False)
        self.log_message("💥 TODAS AS CHAMADAS FORAM DERRUBADAS PELO USUÁRIO (Kill All).", "ERROR")
        self.lbl_status.configure(text="⚠️ Todas as chamadas foram derrubadas.")
        messagebox.showinfo("Derrubar Chamadas", "Todas as instâncias e processos do SIPp foram encerrados com sucesso.")
