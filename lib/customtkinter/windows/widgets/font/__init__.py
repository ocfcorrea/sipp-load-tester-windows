import os
import sys

from .ctk_font import CTkFont
from .font_manager import FontManager
from ..core_rendering import DrawEngine

FontManager.init_font_manager()

customtkinter_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    FontManager.load_font(os.path.join(customtkinter_directory, "assets", "fonts", "Roboto", "Roboto-Regular.ttf"))
    FontManager.load_font(os.path.join(customtkinter_directory, "assets", "fonts", "Roboto", "Roboto-Medium.ttf"))
    FontManager.load_font(os.path.join(customtkinter_directory, "assets", "fonts", "CustomTkinter_shapes_font.otf"))
except Exception:
    pass

# Ensure polygon_shapes is used for native vector rendering
DrawEngine.preferred_drawing_method = "polygon_shapes"
