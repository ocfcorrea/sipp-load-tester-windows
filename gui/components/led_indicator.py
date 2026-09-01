"""
LED Indicator Component - Widget visual de status com LED colorido e texto explicativo.
Estilo Slate / Dark Navy Suave com alto contraste e brilho luminoso.
"""

import tkinter as tk
import customtkinter as ctk


class LedIndicator(ctk.CTkFrame):
    """Componente que desenha um LED luminoso (Verde, Vermelho, Amarelo, Cinza) com rótulo."""

    COLORS = {
        "gray": {"outer": "#383c4e", "inner": "#64748b", "glow": "#212430"},
        "yellow": {"outer": "#b45309", "inner": "#fbbf24", "glow": "#451a03"},
        "green": {"outer": "#15803d", "inner": "#22c55e", "glow": "#052e16"},
        "red": {"outer": "#b91c1c", "inner": "#ef4444", "glow": "#450a0a"},
    }

    def __init__(self, master, label_text: str = "Status do Registro", bg_parent: str = "#272a37", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.current_state = "gray"
        self.message = "Não testado"
        self.bg_parent = bg_parent

        # Canvas para desenhar o círculo com gradiente / brilho
        self.canvas_size = 28
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=self.bg_parent,
            bd=0,
            highlightthickness=0
        )
        self.canvas.pack(side="left", padx=(0, 12))

        # Texto do status
        self.text_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.text_frame.pack(side="left", fill="x", expand=True)

        self.title_label = ctk.CTkLabel(
            self.text_frame,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f1f5f9",
            anchor="w"
        )
        self.title_label.pack(fill="x")

        self.status_label = ctk.CTkLabel(
            self.text_frame,
            text=self.message,
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
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
            9, 9, 13, 13,
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
            self.status_label.configure(text_color="#94a3b8")
