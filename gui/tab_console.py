"""
Tab Console - Aba 3: Console de Execução em Tempo Real, Métricas de Simultaneidade e Controles.
Estilo Shadcn Luna Minimalista com paleta de cores neutras e botões suaves.
"""

from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk

from core.config_manager import ConfigManager
from core.sipp_engine import SippEngine
from gui.components.metric_card import MetricCard


class TabConsole(ctk.CTkFrame):
    """Aba com métricas em tempo real, console de log e painel de controle em cores neutras."""

    def __init__(
        self,
        master,
        config_mgr: ConfigManager,
        sipp_engine: SippEngine,
        start_load_fn=None,
        kill_all_fn=None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.config_mgr = config_mgr
        self.sipp_engine = sipp_engine
        self.start_load_fn = start_load_fn
        self.kill_all_fn = kill_all_fn

        self.max_log_lines = 1500
        self.log_buffer = []

        self._build_ui()

    def _build_ui(self):
        # -------------------------------------------------------------
        # 1. LINHA DE CARDS DE MÉTRICAS (Cores Neutras e Suaves)
        # -------------------------------------------------------------
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=(8, 4))
        metrics_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.card_simult = MetricCard(
            metrics_frame,
            title="Simultâneas Ativas",
            value="0",
            unit="/ 100",
            accent_color="#38bdf8",  # Soft Sky Slate
            icon="📞"
        )
        self.card_simult.grid(row=0, column=0, sticky="ew", padx=4)

        self.card_total = MetricCard(
            metrics_frame,
            title="Total Disparadas",
            value="0",
            unit="ch",
            accent_color="#a1a1aa",  # Neutral Zinc
            icon="📈"
        )
        self.card_total.grid(row=0, column=1, sticky="ew", padx=4)

        self.card_success = MetricCard(
            metrics_frame,
            title="Atendidas (200 OK)",
            value="0",
            unit="ok",
            accent_color="#4ade80",  # Soft Emerald
            icon="✅"
        )
        self.card_success.grid(row=0, column=2, sticky="ew", padx=4)

        self.card_failed = MetricCard(
            metrics_frame,
            title="Falhas / Timeouts",
            value="0",
            unit="err",
            accent_color="#f87171",  # Soft Rose
            icon="❌"
        )
        self.card_failed.grid(row=0, column=3, sticky="ew", padx=4)

        self.card_cps = MetricCard(
            metrics_frame,
            title="Taxa Instantânea",
            value="0.0",
            unit="cps",
            accent_color="#fbbf24",  # Soft Amber
            icon="⚡"
        )
        self.card_cps.grid(row=0, column=4, sticky="ew", padx=4)

        # -------------------------------------------------------------
        # 2. CONSOLE DE LOGS (Shadcn Container)
        # -------------------------------------------------------------
        console_container = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        console_container.pack(fill="both", expand=True, padx=10, pady=6)

        # Barra de ferramentas do console
        toolbar = ctk.CTkFrame(console_container, fg_color="transparent")
        toolbar.pack(fill="x", padx=10, pady=(8, 4))

        lbl_console = ctk.CTkLabel(
            toolbar,
            text="🖥️ Console de Execução & Logs do SIPp",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f4f4f5"
        )
        lbl_console.pack(side="left", padx=4)

        btn_clear = ctk.CTkButton(
            toolbar,
            text="🧹 Limpar",
            width=70,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self.clear_logs
        )
        btn_clear.pack(side="right", padx=3)

        btn_copy = ctk.CTkButton(
            toolbar,
            text="📋 Copiar",
            width=70,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self.copy_logs
        )
        btn_copy.pack(side="right", padx=3)

        btn_export = ctk.CTkButton(
            toolbar,
            text="💾 Exportar",
            width=70,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self.export_logs
        )
        btn_export.pack(side="right", padx=3)

        # Caixa de texto do console (Dark Zinc minimalista)
        self.log_textbox = ctk.CTkTextbox(
            console_container,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none",
            corner_radius=6,
            fg_color="#09090b",
            text_color="#e4e4e7",
            border_width=1,
            border_color="#27272a"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(2, 10))

        # -------------------------------------------------------------
        # 3. BARRA DE CONTROLE DE EXECUÇÃO (Botões Menos Fortes / Suaves)
        # -------------------------------------------------------------
        control_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        control_card.pack(fill="x", padx=10, pady=(2, 8))

        ctrl_inner = ctk.CTkFrame(control_card, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=12, pady=10)
        ctrl_inner.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Botão Iniciar Teste de Carga (Shadcn Primary)
        self.btn_start = ctk.CTkButton(
            ctrl_inner,
            text="🚀 INICIAR TESTE DE CARGA",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#fafafa",
            hover_color="#e4e4e7",
            text_color="#18181b",
            height=36,
            corner_radius=6,
            command=self._on_start_load
        )
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=6)

        # Botão Pausar / Retomar (Muted Amber)
        self.btn_pause = ctk.CTkButton(
            ctrl_inner,
            text="⏸️ Pausar ('p')",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#fbbf24",
            border_width=1,
            border_color="#78350f",
            height=36,
            corner_radius=6,
            state="disabled",
            command=self._on_pause_resume
        )
        self.btn_pause.grid(row=0, column=1, sticky="ew", padx=6)

        # Botão Parar Suave (Muted Orange)
        self.btn_soft_stop = ctk.CTkButton(
            ctrl_inner,
            text="🛑 Parar Suave ('q')",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#fb923c",
            border_width=1,
            border_color="#7c2d12",
            height=36,
            corner_radius=6,
            state="disabled",
            command=self._on_soft_stop
        )
        self.btn_soft_stop.grid(row=0, column=2, sticky="ew", padx=6)

        # Botão Emergência: Derrubar Todas as Chamadas (Muted Red / Destructive)
        self.btn_kill = ctk.CTkButton(
            ctrl_inner,
            text="💥 DERRUBAR TODAS",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#27272a",
            hover_color="#3f1414",
            text_color="#f87171",
            border_width=1,
            border_color="#7f1d1d",
            height=36,
            corner_radius=6,
            command=self._on_kill_all
        )
        self.btn_kill.grid(row=0, column=3, sticky="ew", padx=6)

    def log(self, message: str, level: str = "INFO"):
        """Adiciona uma mensagem formatada ao console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] [{level}] " if level != "STDOUT" else f"[{timestamp}] "
        full_line = f"{prefix}{message}\n"

        self.log_buffer.append(full_line)
        if len(self.log_buffer) > self.max_log_lines:
            self.log_buffer.pop(0)

        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", full_line)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def update_metrics(self, stats: dict):
        """Atualiza os cartões de métricas na tela."""
        active = stats.get("active_calls", 0)
        max_sim = stats.get("max_simultaneas", 100)
        total = stats.get("total_calls", 0)
        succ = stats.get("successful_calls", 0)
        failed = stats.get("failed_calls", 0)
        cps = stats.get("cps", 0.0)

        self.card_simult.set_value(str(active), unit=f"/ {max_sim}")
        self.card_total.set_value(str(total), unit="ch")
        self.card_success.set_value(str(succ), unit="ok")
        self.card_failed.set_value(str(failed), unit="err")
        self.card_cps.set_value(f"{cps:.1f}", unit="cps")

    def reset_metrics(self, max_sim: int = 100):
        """Reseta todos os cartões de métricas para zero."""
        self.card_simult.set_value("0", unit=f"/ {max_sim}")
        self.card_total.set_value("0", unit="ch")
        self.card_success.set_value("0", unit="ok")
        self.card_failed.set_value("0", unit="err")
        self.card_cps.set_value("0.0", unit="cps")

    def set_execution_state(self, running: bool):
        """Atualiza o estado dos botões conforme a execução."""
        if running:
            self.btn_start.configure(state="disabled", text="⚡ TESTE EM EXECUÇÃO...", fg_color="#27272a", text_color="#71717a")
            self.btn_pause.configure(state="normal", text="⏸️ Pausar ('p')")
            self.btn_soft_stop.configure(state="normal")
        else:
            self.btn_start.configure(state="normal", text="🚀 INICIAR TESTE DE CARGA", fg_color="#fafafa", text_color="#18181b")
            self.btn_pause.configure(state="disabled", text="⏸️ Pausar ('p')")
            self.btn_soft_stop.configure(state="disabled")

    def _on_start_load(self):
        if self.start_load_fn:
            self.start_load_fn()

    def _on_pause_resume(self):
        ok = self.sipp_engine.pause_resume()
        if ok:
            if self.sipp_engine.is_paused:
                self.btn_pause.configure(text="▶️ Retomar ('p')", text_color="#4ade80", border_color="#166534")
                self.log("⏸️ Criação de novas chamadas pausada.", "WARNING")
            else:
                self.btn_pause.configure(text="⏸️ Pausar ('p')", text_color="#fbbf24", border_color="#78350f")
                self.log("▶️ Criação de chamadas retomada.", "INFO")

    def _on_soft_stop(self):
        ok = self.sipp_engine.soft_stop()
        if ok:
            self.log("🛑 Saída suave solicitada ('q'). Aguardando chamadas ativas encerrarem...", "WARNING")
            self.btn_soft_stop.configure(state="disabled")

    def _on_kill_all(self):
        if self.kill_all_fn:
            self.kill_all_fn()

    def clear_logs(self):
        self.log_buffer.clear()
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def copy_logs(self):
        text = "".join(self.log_buffer)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copiado", "Logs copiados para a área de transferência.")

    def export_logs(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Arquivos de Log", "*.log"), ("Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
            title="Exportar Logs de Execução"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(self.log_buffer)
                messagebox.showinfo("Sucesso", f"Logs salvos com sucesso em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo: {e}")
