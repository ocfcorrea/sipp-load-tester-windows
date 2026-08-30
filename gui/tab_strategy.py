"""
Tab Strategy - Aba 2: Estratégia de Discagem, Pesos de Destino e Simulação Randômica Humana.
Estilo Shadcn Luna Minimalista com cores neutras.
"""

from tkinter import messagebox
import customtkinter as ctk

from core.config_manager import ConfigManager
from core.strategy_manager import StrategyManager
from gui.components.destination_table import DestinationTable


class TabStrategy(ctk.CTkScrollableFrame):
    """Aba para configuração de capacidade, modos de discagem e tabela de destinos com pesos."""

    def __init__(self, master, config_mgr: ConfigManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.config_mgr = config_mgr
        self._build_ui()
        self.load_from_config()

    def _build_ui(self):
        # -------------------------------------------------------------
        # CARD 1: CAPACIDADE & DURAÇÃO DA CHAMADA
        # -------------------------------------------------------------
        cap_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        cap_card.pack(fill="x", padx=10, pady=8)

        lbl_cap_title = ctk.CTkLabel(
            cap_card,
            text="⚙️ Capacidade & Duração das Chamadas",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f4f4f5"
        )
        lbl_cap_title.pack(anchor="w", padx=16, pady=(14, 6))

        grid_cap = ctk.CTkFrame(cap_card, fg_color="transparent")
        grid_cap.pack(fill="x", padx=16, pady=6)
        grid_cap.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Simultâneas (-l)
        f_simult = ctk.CTkFrame(grid_cap, fg_color="transparent")
        f_simult.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        ctk.CTkLabel(f_simult, text="Simultâneas (-l)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_simultaneas = ctk.CTkEntry(f_simult, placeholder_text="100", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_simultaneas.pack(fill="x", pady=(2, 0))

        # Total de chamadas (-m)
        f_total = ctk.CTkFrame(grid_cap, fg_color="transparent")
        f_total.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        ctk.CTkLabel(f_total, text="Total (-m) [0=Ilimitado]*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_total = ctk.CTkEntry(f_total, placeholder_text="0", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_total.pack(fill="x", pady=(2, 0))

        # Duração Mínima (ms)
        f_dur_min = ctk.CTkFrame(grid_cap, fg_color="transparent")
        f_dur_min.grid(row=0, column=2, sticky="ew", padx=4, pady=4)
        ctk.CTkLabel(f_dur_min, text="Duração Mínima (ms)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_dur_min = ctk.CTkEntry(f_dur_min, placeholder_text="10000", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_dur_min.pack(fill="x", pady=(2, 0))

        # Duração Máxima (ms)
        f_dur_max = ctk.CTkFrame(grid_cap, fg_color="transparent")
        f_dur_max.grid(row=0, column=3, sticky="ew", padx=4, pady=4)
        ctk.CTkLabel(f_dur_max, text="Duração Máxima (ms)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_dur_max = ctk.CTkEntry(f_dur_max, placeholder_text="60000", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_dur_max.pack(fill="x", pady=(2, 0))

        # Switch Duração Fixa
        self.chk_dur_fixa_var = ctk.BooleanVar(value=False)
        self.chk_dur_fixa = ctk.CTkCheckBox(
            cap_card,
            text="Duração Fixa (ignora teto máximo e fixa no valor mínimo)",
            variable=self.chk_dur_fixa_var,
            font=ctk.CTkFont(size=12),
            text_color="#a1a1aa",
            fg_color="#3f3f46",
            hover_color="#52525b",
            border_color="#52525b",
            command=self._on_dur_fixa_toggle
        )
        self.chk_dur_fixa.pack(anchor="w", padx=20, pady=(4, 14))

        # -------------------------------------------------------------
        # CARD 2: MODO DE DISCAGEM & SIMULAÇÃO HUMANA RANDÔMICA
        # -------------------------------------------------------------
        mode_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        mode_card.pack(fill="x", padx=10, pady=8)

        lbl_mode_title = ctk.CTkLabel(
            mode_card,
            text="🎲 Modo de Discagem & Padrão de Disparo",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f4f4f5"
        )
        lbl_mode_title.pack(anchor="w", padx=16, pady=(14, 6))

        # Seletor de Modo
        self.mode_selector = ctk.CTkSegmentedButton(
            mode_card,
            values=["⚡ Taxa Constante (Rate/Period)", "👥 Simulação Humana (Orgânico / Randômico)"],
            fg_color="#09090b",
            selected_color="#27272a",
            selected_hover_color="#3f3f46",
            unselected_hover_color="#27272a",
            text_color="#f4f4f5",
            command=self._on_mode_change
        )
        self.mode_selector.pack(fill="x", padx=16, pady=(2, 10))

        # Painel 1: Taxa Constante
        self.frame_rate_mode = ctk.CTkFrame(mode_card, fg_color="transparent")
        self.frame_rate_mode.pack(fill="x", padx=16, pady=(0, 12))
        self.frame_rate_mode.grid_columnconfigure((0, 1), weight=1)

        f_rate = ctk.CTkFrame(self.frame_rate_mode, fg_color="transparent")
        f_rate.grid(row=0, column=0, sticky="ew", padx=6)
        ctk.CTkLabel(f_rate, text="Novas Chamadas por Período (-r)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_rate = ctk.CTkEntry(f_rate, placeholder_text="50", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_rate.pack(fill="x", pady=(2, 0))

        f_period = ctk.CTkFrame(self.frame_rate_mode, fg_color="transparent")
        f_period.grid(row=0, column=1, sticky="ew", padx=6)
        ctk.CTkLabel(f_period, text="Período da Taxa em ms (-rp)*", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_rate_period = ctk.CTkEntry(f_period, placeholder_text="1000", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_rate_period.pack(fill="x", pady=(2, 0))

        # Painel 2: Simulação Humana / Randômica
        self.frame_human_mode = ctk.CTkFrame(mode_card, fg_color="transparent")
        self.frame_human_mode.grid_columnconfigure((0, 1, 2, 3), weight=1)

        f_h_min = ctk.CTkFrame(self.frame_human_mode, fg_color="transparent")
        f_h_min.grid(row=0, column=0, sticky="ew", padx=4)
        ctk.CTkLabel(f_h_min, text="Intervalo Mín (ms)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_human_min = ctk.CTkEntry(f_h_min, placeholder_text="200", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_human_min.pack(fill="x", pady=(2, 0))

        f_h_max = ctk.CTkFrame(self.frame_human_mode, fg_color="transparent")
        f_h_max.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(f_h_max, text="Intervalo Máx (ms)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_human_max = ctk.CTkEntry(f_h_max, placeholder_text="1500", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_human_max.pack(fill="x", pady=(2, 0))

        f_h_burst = ctk.CTkFrame(self.frame_human_mode, fg_color="transparent")
        f_h_burst.grid(row=0, column=2, sticky="ew", padx=4)
        ctk.CTkLabel(f_h_burst, text="Chance de Pico (%)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_human_burst = ctk.CTkEntry(f_h_burst, placeholder_text="15", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_human_burst.pack(fill="x", pady=(2, 0))

        f_h_token = ctk.CTkFrame(self.frame_human_mode, fg_color="transparent")
        f_h_token.grid(row=0, column=3, sticky="ew", padx=4)
        ctk.CTkLabel(f_h_token, text="Prefixo de Token", font=ctk.CTkFont(size=12, weight="bold"), text_color="#a1a1aa").pack(anchor="w")
        self.entry_human_token = ctk.CTkEntry(f_h_token, placeholder_text="AGENT_", fg_color="#09090b", border_color="#27272a", text_color="#f4f4f5")
        self.entry_human_token.pack(fill="x", pady=(2, 0))

        # -------------------------------------------------------------
        # CARD 3: TABELA DE DESTINOS COM PESOS E PRIORIDADES
        # -------------------------------------------------------------
        dest_card = ctk.CTkFrame(self, corner_radius=8, fg_color="#18181b", border_width=1, border_color="#27272a")
        dest_card.pack(fill="x", padx=10, pady=8)

        self.dest_table = DestinationTable(dest_card, height=340, on_change_callback=self._on_table_change)
        self.dest_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Botões de Ação para Destinos (Shadcn Luna Neutral Buttons)
        btn_bar = ctk.CTkFrame(dest_card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=14, pady=(0, 14))

        btn_equal = ctk.CTkButton(
            btn_bar,
            text="⚖️ Distribuir Pesos Igualmente",
            font=ctk.CTkFont(size=12),
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self._distribute_equal_weights
        )
        btn_equal.pack(side="left", padx=4)

        btn_clear = ctk.CTkButton(
            btn_bar,
            text="🧹 Limpar Desmarcados",
            font=ctk.CTkFont(size=12),
            fg_color="#27272a",
            hover_color="#3f3f46",
            text_color="#f4f4f5",
            border_width=1,
            border_color="#3f3f46",
            command=self._clear_disabled
        )
        btn_clear.pack(side="left", padx=4)

        btn_save = ctk.CTkButton(
            btn_bar,
            text="💾 Salvar Estratégia",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#fafafa",
            hover_color="#e4e4e7",
            text_color="#18181b",
            command=self.save_to_config
        )
        btn_save.pack(side="right", padx=4)

    def _on_dur_fixa_toggle(self):
        is_fixa = self.chk_dur_fixa_var.get()
        if is_fixa:
            self.entry_dur_max.configure(state="disabled")
        else:
            self.entry_dur_max.configure(state="normal")

    def _on_mode_change(self, selected_mode: str):
        if "Humana" in selected_mode or "Orgânico" in selected_mode:
            self.frame_rate_mode.pack_forget()
            self.frame_human_mode.pack(fill="x", padx=16, pady=(0, 12))
        else:
            self.frame_human_mode.pack_forget()
            self.frame_rate_mode.pack(fill="x", padx=16, pady=(0, 12))

    def _on_table_change(self):
        pass

    def _distribute_equal_weights(self):
        for row in self.dest_table.rows:
            if row["chk_var"].get() and row["entry_number"].get().strip():
                row["slider_weight"].set(10)
                row["lbl_weight_val"].configure(text="10")
        self.dest_table.recalculate_percentages()

    def _clear_disabled(self):
        for row in self.dest_table.rows:
            if not row["chk_var"].get():
                row["entry_number"].delete(0, "end")
                row["entry_desc"].delete(0, "end")
                row["slider_weight"].set(10)
                row["lbl_weight_val"].configure(text="10")
        self.dest_table.recalculate_percentages()

    def load_from_config(self):
        cfg = self.config_mgr.config

        self.entry_simultaneas.delete(0, "end")
        self.entry_simultaneas.insert(0, str(cfg.get("simultaneas", 100)))

        self.entry_total.delete(0, "end")
        self.entry_total.insert(0, str(cfg.get("total", 0)))

        self.entry_dur_min.delete(0, "end")
        self.entry_dur_min.insert(0, str(cfg.get("duracao_min_ms", 10000)))

        self.entry_dur_max.delete(0, "end")
        self.entry_dur_max.insert(0, str(cfg.get("duracao_max_ms", 60000)))

        is_fixa = bool(cfg.get("duracao_fixa", False))
        self.chk_dur_fixa_var.set(is_fixa)
        self._on_dur_fixa_toggle()

        self.entry_rate.delete(0, "end")
        self.entry_rate.insert(0, str(cfg.get("rate", 50)))

        self.entry_rate_period.delete(0, "end")
        self.entry_rate_period.insert(0, str(cfg.get("rate_period", 1000)))

        self.entry_human_min.delete(0, "end")
        self.entry_human_min.insert(0, str(cfg.get("human_min_interval_ms", 200)))

        self.entry_human_max.delete(0, "end")
        self.entry_human_max.insert(0, str(cfg.get("human_max_interval_ms", 1500)))

        self.entry_human_burst.delete(0, "end")
        self.entry_human_burst.insert(0, str(cfg.get("human_burst_chance", 15)))

        self.entry_human_token.delete(0, "end")
        self.entry_human_token.insert(0, str(cfg.get("human_token_prefix", "AGENT_")))

        mode = cfg.get("dial_mode", "rate")
        if mode == "human_random":
            self.mode_selector.set("👥 Simulação Humana (Orgânico / Randômico)")
            self._on_mode_change("👥 Simulação Humana (Orgânico / Randômico)")
        else:
            self.mode_selector.set("⚡ Taxa Constante (Rate/Period)")
            self._on_mode_change("⚡ Taxa Constante (Rate/Period)")

        self.dest_table.populate(cfg.get("destinations", []))

    def save_to_config(self):
        try:
            self.config_mgr.set("simultaneas", int(self.entry_simultaneas.get().strip() or 100))
            self.config_mgr.set("total", int(self.entry_total.get().strip() or 0))
            self.config_mgr.set("duracao_min_ms", int(self.entry_dur_min.get().strip() or 10000))
            self.config_mgr.set("duracao_max_ms", int(self.entry_dur_max.get().strip() or 60000))
            self.config_mgr.set("duracao_fixa", self.chk_dur_fixa_var.get())

            mode_str = self.mode_selector.get()
            dial_mode = "human_random" if "Humana" in mode_str or "Orgânico" in mode_str else "rate"
            self.config_mgr.set("dial_mode", dial_mode)

            self.config_mgr.set("rate", int(self.entry_rate.get().strip() or 50))
            self.config_mgr.set("rate_period", int(self.entry_rate_period.get().strip() or 1000))

            self.config_mgr.set("human_min_interval_ms", int(self.entry_human_min.get().strip() or 200))
            self.config_mgr.set("human_max_interval_ms", int(self.entry_human_max.get().strip() or 1500))
            self.config_mgr.set("human_burst_chance", int(self.entry_human_burst.get().strip() or 15))
            self.config_mgr.set("human_token_prefix", self.entry_human_token.get().strip() or "AGENT_")

            dests_data = self.dest_table.get_data()
            self.config_mgr.set("destinations", dests_data)

            self.config_mgr.save_config()
            return True
        except ValueError as e:
            messagebox.showerror("Erro de Formato", f"Verifique os campos numéricos: {e}")
            return False
