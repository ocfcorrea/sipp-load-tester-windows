"""
Destination Table Component - Tabela interativa para gerenciar até 10 destinos com pesos e prioridades.
Estilo Slate / Dark Navy Suave com cálculo de porcentagem em tempo real.
"""

from typing import List, Dict, Any, Callable
import customtkinter as ctk


class DestinationTable(ctk.CTkScrollableFrame):
    """Componente que exibe e gerencia a lista de destinos com pesos e prioridades."""

    def __init__(self, master, on_change_callback: Callable = None, **kwargs):
        super().__init__(
            master,
            label_text="🎯 Lista de Destinos & Prioridades de Discagem (1 a 10)",
            fg_color="#272a37",
            label_fg_color="#272a37",
            label_text_color="#f1f5f9",
            border_width=1,
            border_color="#383c4e",
            corner_radius=8,
            **kwargs
        )

        self.on_change_callback = on_change_callback
        self.rows = []

        self._build_header()

    def _build_header(self):
        """Cria o cabeçalho da tabela."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=4, pady=(2, 6))

        col_w = [25, 45, 160, 180, 180, 80]
        
        ctk.CTkLabel(header_frame, text="#", width=col_w[0], font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8").pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Ativo", width=col_w[1], font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8").pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Número Destino*", width=col_w[2], font=ctk.CTkFont(size=11, weight="bold"), anchor="w", text_color="#94a3b8").pack(side="left", padx=4)
        ctk.CTkLabel(header_frame, text="Descrição / Identificador", width=col_w[3], font=ctk.CTkFont(size=11, weight="bold"), anchor="w", text_color="#94a3b8").pack(side="left", padx=4)
        ctk.CTkLabel(header_frame, text="Peso / Prioridade (1-100)", width=col_w[4], font=ctk.CTkFont(size=11, weight="bold"), anchor="w", text_color="#94a3b8").pack(side="left", padx=4)
        ctk.CTkLabel(header_frame, text="Proporção", width=col_w[5], font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8").pack(side="left", padx=4)

    def populate(self, destinations: List[Dict[str, Any]]):
        """Popula as 10 linhas da tabela com os dados fornecidos."""
        for row in self.rows:
            row["frame"].destroy()
        self.rows.clear()

        dests = list(destinations)
        while len(dests) < 10:
            dests.append({"enabled": False, "number": "", "description": "", "weight": 10})

        for i, item in enumerate(dests[:10]):
            self._create_row(i + 1, item)

        self.recalculate_percentages()

    def _create_row(self, index: int, data: Dict[str, Any]):
        """Cria uma linha para a tabela."""
        row_bg = "#212430" if index % 2 == 0 else "#1a1c26"
        row_frame = ctk.CTkFrame(self, fg_color=row_bg, corner_radius=6, border_width=1, border_color="#383c4e")
        row_frame.pack(fill="x", padx=2, pady=2)

        # 1. Índice
        lbl_idx = ctk.CTkLabel(row_frame, text=str(index), width=25, font=ctk.CTkFont(size=11), text_color="#94a3b8")
        lbl_idx.pack(side="left", padx=2)

        # 2. Checkbox Ativo
        chk_var = ctk.BooleanVar(value=data.get("enabled", False))
        chk = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=chk_var,
            width=35,
            fg_color="#0284c7",
            hover_color="#0369a1",
            border_color="#475569",
            command=self._on_field_change
        )
        chk.pack(side="left", padx=4)

        # 3. Número Destino
        entry_num = ctk.CTkEntry(
            row_frame,
            width=160,
            height=28,
            font=ctk.CTkFont(size=12),
            placeholder_text="Ex: 22223333",
            fg_color="#1e202b",
            border_color="#383c4e",
            text_color="#f1f5f9"
        )
        if data.get("number"):
            entry_num.insert(0, str(data["number"]))
        entry_num.pack(side="left", padx=4)
        entry_num.bind("<KeyRelease>", lambda e: self._on_field_change())

        # 4. Descrição
        entry_desc = ctk.CTkEntry(
            row_frame,
            width=180,
            height=28,
            font=ctk.CTkFont(size=12),
            placeholder_text="Ex. Texto para Identificar",
            fg_color="#1e202b",
            border_color="#383c4e",
            text_color="#f1f5f9"
        )
        if data.get("description"):
            entry_desc.insert(0, str(data["description"]))
        entry_desc.pack(side="left", padx=4)

        # 5. Slider + Label de Peso
        slider_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=180)
        slider_frame.pack(side="left", padx=4)

        weight_val = max(1, min(100, int(data.get("weight", 10))))
        lbl_weight_val = ctk.CTkLabel(slider_frame, text=f"{weight_val:3d}", width=32, font=ctk.CTkFont(size=11, weight="bold"), text_color="#38bdf8")
        lbl_weight_val.pack(side="right", padx=(2, 0))

        def _on_slider(val, lbl=lbl_weight_val):
            ival = int(round(float(val)))
            lbl.configure(text=f"{ival:3d}")
            self.recalculate_percentages()
            if self.on_change_callback:
                self.on_change_callback()

        slider = ctk.CTkSlider(
            slider_frame,
            from_=1,
            to=100,
            number_of_steps=99,
            width=135,
            fg_color="#383c4e",
            progress_color="#0284c7",
            button_color="#38bdf8",
            button_hover_color="#7dd3fc",
            command=_on_slider
        )
        slider.set(weight_val)
        slider.pack(side="left", padx=(0, 2))

        # 6. Proporção calculada em %
        lbl_pct = ctk.CTkLabel(
            row_frame,
            text="0.0%",
            width=80,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#38bdf8"
        )
        lbl_pct.pack(side="left", padx=4)

        self.rows.append({
            "frame": row_frame,
            "chk_var": chk_var,
            "entry_num": entry_num,
            "entry_desc": entry_desc,
            "slider": slider,
            "lbl_weight_val": lbl_weight_val,
            "lbl_pct": lbl_pct
        })

    def _on_field_change(self):
        """Disparado quando há alteração nos campos da tabela."""
        self.recalculate_percentages()
        if self.on_change_callback:
            self.on_change_callback()

    def recalculate_percentages(self):
        """Calcula e atualiza visualmente o percentual de tráfego de cada destino ativo."""
        active_dests = []
        for r in self.rows:
            is_enabled = r["chk_var"].get()
            num = r["entry_num"].get().strip()
            weight = int(round(r["slider"].get()))
            if is_enabled and num:
                active_dests.append({"weight": weight, "row_ref": r})
            else:
                r["lbl_pct"].configure(text="—", text_color="#64748b")

        if not active_dests:
            return

        total_w = sum(d["weight"] for d in active_dests)
        for d in active_dests:
            pct = (d["weight"] / total_w) * 100.0 if total_w > 0 else 0.0
            d["row_ref"]["lbl_pct"].configure(text=f"{pct:5.1f}%", text_color="#38bdf8")

    def get_destinations(self) -> List[Dict[str, Any]]:
        """Retorna os destinos estruturados prontos para salvar no ConfigManager."""
        dest_list = []
        for r in self.rows:
            dest_list.append({
                "enabled": r["chk_var"].get(),
                "number": r["entry_num"].get().strip(),
                "description": r["entry_desc"].get().strip(),
                "weight": int(round(r["slider"].get()))
            })
        return dest_list

    def get_data(self) -> List[Dict[str, Any]]:
        """Alias para get_destinations."""
        return self.get_destinations()
