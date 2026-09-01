"""
Metric Card Component - Cartão de métricas estilo Slate / Dark Navy Suave.
"""

from typing import Any
import customtkinter as ctk


class MetricCard(ctk.CTkFrame):
    """Cartão de exibição de indicador numérico com estética Slate moderna."""

    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        unit: str = "",
        accent_color: str = "#38bdf8",
        icon: str = "📊",
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=8,
            fg_color="#272a37",
            border_width=1,
            border_color="#383c4e",
            **kwargs
        )

        self.accent_color = accent_color
        self.unit = unit

        self.grid_columnconfigure(1, weight=1)
        
        # Barra lateral suave de destaque
        self.stripe = ctk.CTkFrame(self, width=3, corner_radius=2, fg_color=accent_color)
        self.stripe.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(6, 8), pady=8)

        # Cabeçalho com ícone e título
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(8, 0))

        self.icon_label = ctk.CTkLabel(
            self.header_frame,
            text=icon,
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        )
        self.icon_label.pack(side="left", padx=(0, 6))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8"
        )
        self.title_label.pack(side="left")

        # Valor numérico principal
        self.value_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.value_frame.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 8))

        self.value_label = ctk.CTkLabel(
            self.value_frame,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f1f5f9"
        )
        self.value_label.pack(side="left")

        if unit:
            self.unit_label = ctk.CTkLabel(
                self.value_frame,
                text=f" {unit}",
                font=ctk.CTkFont(size=11),
                text_color="#64748b"
            )
            self.unit_label.pack(side="left", padx=(4, 0))

    def set_value(self, new_value: Any, unit: str = None):
        """Atualiza o valor exibido no cartão."""
        self.value_label.configure(text=str(new_value))
        if unit is not None and hasattr(self, 'unit_label'):
            self.unit_label.configure(text=f" {unit}")
