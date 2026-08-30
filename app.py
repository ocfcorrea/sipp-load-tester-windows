#!/usr/bin/env python3
"""
SIPp Load Tester Pro - Interface Gráfica para Testes de Chamadas SIP Simultâneas
Desenvolvido para L5 Networks
"""

import sys
import os

# Ajusta DPI awareness no Windows para renderização nítida
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
