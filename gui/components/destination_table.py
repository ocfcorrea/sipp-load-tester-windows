"""
Destination Table Component - Tabela interativa para gerenciar até 10 destinos com pesos e prioridades.
Estilo Shadcn Luna Minimalista com cores neutras e cálculo de porcentagem em tempo real.
"""

from typing import List, Dict, Any, Callable
import customtkinter as ctk
from core.strategy_manager import StrategyManager


class DestinationTable(ctk.CTkScrollableFrame):
    """Componente que exibe e gerencia a lista de destinos com pesos e prioridades."""

    def __init__(self, master, on_change_callback: Callable = None, **kwargs):
        super().__init__(
            master,
            label_text="🎯 Lista de Destinos & Prioridades de Discagem (1 a 10)",
            fg_color="#18181b",
            label_fg_color="#18181b",
            label_text_color="#f4f4f5",
            border_width=1,
            border_color="#27272a",
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
        
        ctk.CTkLabel(header_frame, text="#", width=col_w[0], font=ctk.CTkFont(size=11, weight="bold"), text_color="#71717a").pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Ativo", width=col_w[1], font=ctk.CTkFont(size=11, weight="bold"), text_color="#71717a").pack(side="left", padx=2)
        ctk.CTkLabel(header_frame, text="Número Destino*", width=col_w[2], font=ctk.CTkFont(size=11, weight="bold"), anchor="w", text_color="#71717a").pack(side="left", padx=4)
        ctk.CTkLabel(header_frame, text="Descrição / Identificador", width=col_w[3], font=ctk.CTkFont(size=11, weight="bold"), anchor="w", text_color="#71717a").pack(side="left", padx=4)
        ctk.CTkLabel(header_frame, text="Peso / Prioridade (1-100)", width=col_w[4], font=ctk.CTkFont(size=11, weight="bold"), anchor="w", text_color="#71717a").pack(side="left", padx=4)
        ctk.CTkLabel(header_frame, text="Proporção", width=col_w[5], font=ctk.CTkFont(size=11, weight="bold"), text_color="#71717a").pack(side="left", padx=4)

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
        row_bg = "#121215" if index % 2 == 0 else "#09090b"
        row_frame = ctk.CTkFrame(self, fg_color=row_bg, corner_radius=6, border_width=1, border_color="#27272a")
        row_frame.pack(fill="x", padx=2, pady=2)

        # 1. Índice
        lbl_idx = ctk.CTkLabel(row_frame, text=str(index), width=25, font=ctk.CTkFont(size=11), text_color="#71717a")
        lbl_idx.pack(side="left", padx=2)

        # 2. Checkbox Ativo
        chk_var = ctk.BooleanVar(value=bool(data.get("enabled", False)))
        chk = ctk.CTkCheckBox(
            row_frame,
            text="",
            variable=chk_var,
            width=24,
            fg_color="#3f3f46",
            hover_color="#52525b",
            border_color="#52525b",
            checkmark_color="#f4f4f5",
            command=self._on_field_change
        )
        chk.pack(side="left", padx=8)

        # 3. Número de Destino
        entry_number = ctk.CTkEntry(
            row_frame,
            placeholder_text=f"Ex: 2222186{index}" if index == 1 else f"Destino {index}",
            width=160,
            height=28,
            fg_color="#09090b",
            border_color="#27272a",
            text_color="#f4f4f5"
        )
        entry_number.insert(0, str(data.get("number", "")))
        entry_number.pack(side="left", padx=4)
        entry_number.bind("<KeyRelease>", lambda e: self._on_field_change())

        # 4. Descrição
        entry_desc = ctk.CTkEntry(
            row_frame,
            placeholder_text="Identificação do ramal/URA",
            width=180,
            height=28,
            fg_color="#09090b",
            border_color="#27272a",
            text_color="#f4f4f5"
        )
        entry_desc.insert(0, str(data.get("description", "")))
        entry_desc.pack(side="left", padx=4)
        entry_desc.bind("<KeyRelease>", lambda e: self._on_field_change())

        # 5. Slider de Peso + Label de valor
        weight_val = int(data.get("weight", 10))
        weight_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=180)
        weight_frame.pack(side="left", padx=4)

        lbl_weight_val = ctk.CTkLabel(weight_frame, text=str(weight_val), width=28, font=ctk.CTkFont(size=11, weight="bold"), text_color="#a1a1aa")
        lbl_weight_val.pack(side="right", padx=(4, 0))

        slider_weight = ctk.CTkSlider(
            weight_frame,
            from_=1,
            to=100,
            number_of_steps=99,
            width=140,
            height=16,
            fg_color="#27272a",
            progress_color="#3f3f46",
            button_color="#f4f4f5",
            button_hover_color="#e4e4e7",
            command=lambda val, lbl=lbl_weight_val: self._on_slider_change(val, lbl)
        )
        slider_weight.set(weight_val)
        slider_weight.pack(side="left")

        # 6. Badge de Porcentagem
        lbl_pct = ctk.CTkLabel(
            row_frame,
            text="0.0%",
            width=70,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#71717a"
        )
        lbl_pct.pack(side="left", padx=6)

        row_data = {
            "frame": row_frame,
            "chk_var": chk_var,
            "entry_number": entry_number,
            "entry_desc": entry_desc,
            "slider_weight": slider_weight,
            "lbl_weight_val": lbl_weight_val,
            "lbl_pct": lbl_pct,
        }
        self.rows.append(row_data)

    def _on_slider_change(self, val: float, lbl: ctk.CTkLabel):
        lbl.configure(text=str(int(val)))
        self.recalculate_percentages()
        if self.on_change_callback:
            self.on_change_callback()

    def _on_field_change(self):
        self.recalculate_percentages()
        if self.on_change_callback:
            self.on_change_callback()

    def recalculate_percentages(self):
        current_data = self.get_data()
        updated = StrategyManager.calculate_weights_percentage(current_data)

        for i, item in enumerate(updated):
            if i < len(self.rows):
                pct = item.get("percentage", 0.0)
                is_active = item.get("enabled") and item.get("number")
                if is_active and pct > 0:
                    self.rows[i]["lbl_pct"].configure(text=f"{pct:.1f}%", text_color="#4ade80")
                else:
                    self.rows[i]["lbl_pct"].configure(text="0.0%", text_color="#52525b")

    def get_data(self) -> List[Dict[str, Any]]:
        data = []
        for r in self.rows:
            data.append({
                "enabled": r["chk_var"].get(),
                "number": r["entry_number"].get().strip(),
                "description": r["entry_desc"].get().strip(),
                "weight": int(r["slider_weight"].get()),
            })
        return data
