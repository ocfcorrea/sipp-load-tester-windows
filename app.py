#!/usr/bin/env python3
"""
SIPp Load Tester Pro - Interface Gráfica para Testes de Chamadas SIP Simultâneas
Desenvolvido para L5 Networks
"""

import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Validação defensiva de dependências essenciais
try:
    import customtkinter as ctk
    from dotenv import load_dotenv
    import PIL
    import packaging
    import darkdetect
except ImportError as e:
    missing_pkg = getattr(e, 'name', str(e))
    error_msg = (
        f"\n[ERRO DE DEPENDÊNCIA] Não foi possível importar o pacote: {missing_pkg}\n\n"
        f"Possível causa: As dependências do projeto não foram instaladas no ambiente Python atual.\n\n"
        f"Como resolver:\n"
        f"  1. No Windows, execute o script: 'iniciar_app.bat' ou 'instalar_dependencias.bat'\n"
        f"  2. Ou instale manualmente via terminal:\n"
        f"       python -m venv .venv\n"
        f"       .\\.venv\\Scripts\\activate\n"
        f"       pip install -r requirements.txt\n"
    )
    print(error_msg, file=sys.stderr)

    # Tenta exibir popup gráfico básico nativo do Tkinter se disponível
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "SIPp Load Tester Pro — Dependência Ausente",
            f"Falta instalar as dependências do Python ({missing_pkg}).\n\n"
            "Por favor, execute o arquivo 'iniciar_app.bat' ou 'instalar_dependencias.bat' para configurar o ambiente automaticamente."
        )
        root.destroy()
    except Exception:
        pass

    sys.exit(1)

# Inicializa gerenciador de caminhos e ambiente .env
from core.paths import ensure_env_file, BASE_DIR
ensure_env_file()

# Ajusta DPI awareness no Windows para renderização nítida
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

from gui.main_window import MainWindow


def main():
    try:
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nAplicação encerrada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro fatal na aplicação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
