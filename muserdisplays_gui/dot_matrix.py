# /home/muser/Desktop/proeject/muserdisplays_gui/dot_matrix_gui.py
import tkinter as tk
from .base_display_gui import GUIDisplay
from .fonts import FONT_5X7 
from typing import List, Dict, Tuple

class DotMatrixDisplayGUI(GUIDisplay):
    """
    A GUI simulation of a single-row dot matrix display.
    """
    CHAR_WIDTH_PX = FONT_5X7["CHAR_WIDTH_PX"]
    CHAR_HEIGHT_PX = FONT_5X7["CHAR_HEIGHT_PX"]

    CHAR_SPACING_PX = 1

    BACKGROUND_COLOR = "black"
    ACTIVE_COLOR = "lime" 

    def __init__(self, canvas: tk.Canvas, num_chars: int = 1, start_x: int = 0, start_y: int = 0):
        super().__init__(canvas, start_x, start_y)
        self.font = FONT_5X7
        self.num_display_chars = num_chars
        self.display_buffer: List[str] = [' '] * self.num_display_chars
        self.PIXEL_SIZE = 5 # This is the scaling factor for the dot matrix display
        
        self.WIDTH_PX = (self.CHAR_WIDTH_PX * self.num_display_chars) + \
                        (self.CHAR_SPACING_PX * (self.num_display_chars - 1))
        self.HEIGHT_PX = self.CHAR_HEIGHT_PX

        # self.pixels here is a dictionary mapping (x, y) to canvas item IDs
        self.pixels: Dict[Tuple[int, int], int] = {} 
        self.render_empty_display()

    def _draw_pixel(self, x: int, y: int, color: str):
        """
        Draws a single 'pixel' (which is a square of PIXEL_SIZE x PIXEL_SIZE)
        on the canvas at the given display coordinates (x, y).
        """
        key = (x, y)
        if key in self.pixels:
            self.canvas.itemconfig(self.pixels[key], fill=color, outline=color)
        else:
            pixel_id = self.canvas.create_rectangle(
                self.start_x + x * self.PIXEL_SIZE, self.start_y + y * self.PIXEL_SIZE,
                self.start_x + (x + 1) * self.PIXEL_SIZE, self.start_y + (y + 1) * self.PIXEL_SIZE,
                fill=color, outline=color 
            )
            self.pixels[key] = pixel_id

    def _draw_char(self, char_index: int, char: str):
        """
        Draws a single character at a specific character position on the dot matrix.
        """
        char_bitmap = self.font.get(char.upper(), self.font[' '])

        # Calculate the starting pixel X for this character
        start_x_px = char_index * (self.CHAR_WIDTH_PX + self.CHAR_SPACING_PX)

        for y_offset in range(self.CHAR_HEIGHT_PX):
            for x_offset in range(self.CHAR_WIDTH_PX):
                bitmap_idx = y_offset * self.CHAR_WIDTH_PX + x_offset
                is_pixel_active = (bitmap_idx < len(char_bitmap) and char_bitmap[bitmap_idx] == '1')
                
                pixel_color = self.ACTIVE_COLOR if is_pixel_active else self.BACKGROUND_COLOR
                self._draw_pixel(start_x_px + x_offset, y_offset, pixel_color)

    def write_text(self, text: str):
        """
        Writes text to the display buffer and triggers a re-render.
        Text will be truncated if it exceeds the number of display characters.
        """
        display_text = text.ljust(self.num_display_chars)[:self.num_display_chars]
        self.display_buffer = list(display_text)
        self.render() 

    def clear(self):
        """Clears the display buffer, effectively turning off all segments."""
        self.write_text(" " * self.num_display_chars) 

    def render_empty_display(self):
        """
        Draws the initial blank background of the dot matrix display area.
        It also clears any existing pixel rectangles on the canvas.
        """
        # Draw the main background rectangle for the entire display area
        self.canvas.create_rectangle(
            self.start_x, self.start_y,
            self.start_x + self.WIDTH_PX * self.PIXEL_SIZE,
            self.start_y + self.HEIGHT_PX * self.PIXEL_SIZE,
            fill=self.BACKGROUND_COLOR, outline=""
        )
        # Clear any existing pixel drawing items from previous renders
        for pixel_id in self.pixels.values():
            self.canvas.delete(pixel_id)
        self.pixels.clear() 

    def render(self):
        """
        Renders the current state of the dot matrix display based on its internal `display_buffer`.
        This method fully overrides the `render()` method from `GUIDisplay`.
        """
        self.render_empty_display()

        for char_idx, char in enumerate(self.display_buffer):
            self._draw_char(char_idx, char)