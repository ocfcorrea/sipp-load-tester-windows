import sys

from .ctk_canvas import CTkCanvas
from .draw_engine import DrawEngine

CTkCanvas.init_font_character_mapping()

# Use polygon_shapes for robust native vector drawing without GDI font loading dependencies
DrawEngine.preferred_drawing_method = "polygon_shapes"
