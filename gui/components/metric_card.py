"""
Metric Card Component - Cartão minimalista estilo Shadcn Luna com cores neutras.
"""

from typing import Any
import customtkinter as ctk


class MetricCard(ctk.CTkFrame):
    """Cartão de exibição de indicador numérico com estética Shadcn Luna neutra."""

    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        unit: str = "",
        accent_color: str = "#3f3f46",
        icon: str = "📊",
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=8,
            fg_color="#18181b",
            border_width=1,
            border_color="#27272a",
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
            text_color="#a1a1aa"
        )
        self.icon_label.pack(side="left", padx=(0, 6))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#71717a"
        )
        self.title_label.pack(side="left")

        # Valor numérico principal
        self.value_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.value_frame.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 8))

        self.value_label = ctk.CTkLabel(
            self.value_frame,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#f4f4f5"
        )
        self.value_label.pack(side="left")

        if unit:
            self.unit_label = ctk.CTkLabel(
                self.value_frame,
                text=f" {unit}",
                font=ctk.CTkFont(size=11),
                text_color="#71717a"
            )
            self.unit_label.pack(side="left", padx=(4, 0))

    def set_value(self, new_value: Any, unit: str = None):
        """Atualiza o valor exibido no cartão."""
        self.value_label.configure(text=str(new_value))
        if unit is not None and hasattr(self, 'unit_label'):
            self.unit_label.configure(text=f" {unit}")
