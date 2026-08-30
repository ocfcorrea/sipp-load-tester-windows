"""
LED Indicator Component - Widget visual de status com LED colorido e texto explicativo.
"""

import tkinter as tk
import customtkinter as ctk


class LedIndicator(ctk.CTkFrame):
    """Componente que desenha um LED luminoso (Verde, Vermelho, Amarelo, Cinza) com rótulo."""

    COLORS = {
        "gray": {"outer": "#27272a", "inner": "#52525b", "glow": "#18181b"},
        "yellow": {"outer": "#78350f", "inner": "#f59e0b", "glow": "#451a03"},
        "green": {"outer": "#14532d", "inner": "#22c55e", "glow": "#052e16"},
        "red": {"outer": "#7f1d1d", "inner": "#ef4444", "glow": "#450a0a"},
    }

    def __init__(self, master, label_text: str = "Status do Registro", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.current_state = "gray"
        self.message = "Não testado"

        # Canvas para desenhar o círculo com gradiente / brilho
        self.canvas_size = 26
        bg_color = "#18181b" if ctk.get_appearance_mode().lower() == "dark" else "#ebebeb"
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=bg_color,
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack(side="left", padx=(0, 10))

        # Texto do status
        self.text_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.text_frame.pack(side="left", fill="x", expand=True)

        self.title_label = ctk.CTkLabel(
            self.text_frame,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f4f4f5",
            anchor="w"
        )
        self.title_label.pack(fill="x")

        self.status_label = ctk.CTkLabel(
            self.text_frame,
            text=self.message,
            font=ctk.CTkFont(size=12),
            text_color="#71717a",
            anchor="w"
        )
        self.status_label.pack(fill="x")

        self.set_state("gray", "Não testado")

    def set_state(self, state: str, message: str = ""):
        """
        Atualiza o estado do LED:
        - 'gray': Inativo / Não testado
        - 'yellow': Verificando / Aguardando
        - 'green': Registrado com Sucesso (200 OK)
        - 'red': Falha / Erro
        """
        self.current_state = state if state in self.COLORS else "gray"
        self.message = message if message else self.message
        
        self.canvas.delete("all")
        colors = self.COLORS[self.current_state]

        # Brilho externo (glow)
        self.canvas.create_oval(
            2, 2, self.canvas_size - 2, self.canvas_size - 2,
            fill=colors["glow"], outline=colors["outer"], width=2
        )
        # Núcleo luminoso interno
        self.canvas.create_oval(
            6, 6, self.canvas_size - 6, self.canvas_size - 6,
            fill=colors["inner"], outline=""
        )
        # Ponto de reflexo de luz
        self.canvas.create_oval(
            8, 8, 12, 12,
            fill="#ffffff", outline=""
        )

        # Atualiza o texto e cor do rótulo
        self.status_label.configure(text=self.message)
        if self.current_state == "green":
            self.status_label.configure(text_color="#4ade80")
        elif self.current_state == "red":
            self.status_label.configure(text_color="#f87171")
        elif self.current_state == "yellow":
            self.status_label.configure(text_color="#fbbf24")
        else:
            self.status_label.configure(text_color="#9da5b4")
