# /home/muser/Desktop/proeject/muserdisplays_gui/ssd1306_128x32_gui.py
import tkinter as tk
from typing import Dict, Tuple

from .base_display_gui import GUIDisplay
from .fonts import FONT_5X7 

class SSD1306_128x32_GUI(GUIDisplay): 
    WIDTH_PX = 128
    HEIGHT_PX = 32 

    CHAR_WIDTH_PX = FONT_5X7["CHAR_WIDTH_PX"]   
    CHAR_HEIGHT_PX = FONT_5X7["CHAR_HEIGHT_PX"] 

    ACTIVE_COLOR = "lightgray"
    INACTIVE_COLOR = "black"

    def __init__(self, canvas: tk.Canvas, start_x: int = 0, start_y: int = 0):
        super().__init__(canvas, start_x, start_y)
        self.font = FONT_5X7 
        self.pixel_buffer = [[0 for _ in range(self.WIDTH_PX)] for _ in range(self.HEIGHT_PX)]
        self.pixels = [] 
        self.PIXEL_SIZE = 2 # Added scaling factor for SSD1306
        self.render_empty_display()

    def set_pixel(self, x_px: int, y_px: int, state: int):
        if x_px < 0 or x_px >= self.WIDTH_PX or y_px < 0 or y_px >= self.HEIGHT_PX:
            return
        self.pixel_buffer[y_px][x_px] = state
        color = self.ACTIVE_COLOR if state == 1 else self.INACTIVE_COLOR
        self.canvas.itemconfig(self.pixels[y_px][x_px], fill=color)

    def draw_char_to_buffer(self, x_px_start: int, y_px_start: int, char: str):
        """
        Draws a single character's bitmap directly into the pixel buffer.
        """
        char_bitmap = self.font.get(char.upper(), self.font[' '])

        for y_offset in range(self.CHAR_HEIGHT_PX):
            for x_offset in range(self.CHAR_WIDTH_PX): 
                bitmap_idx = y_offset * self.font["CHAR_WIDTH_PX"] + x_offset 
                
                if bitmap_idx < len(char_bitmap) and char_bitmap[bitmap_idx] == '1':
                    self.set_pixel(x_px_start + x_offset, y_px_start + y_offset, 1)
                else:
                    self.set_pixel(x_px_start + x_offset, y_px_start + y_offset, 0)

    def write_text(self, row: int, col: int, text: str):
        start_y_px = row * self.CHAR_HEIGHT_PX
        current_x_px = col * self.CHAR_WIDTH_PX
        for char in text:
            self.draw_char_to_buffer(current_x_px, start_y_px, char)
            current_x_px += self.CHAR_WIDTH_PX

    def render_empty_display(self):
        for row_pixels in self.pixels:
            for pixel_id in row_pixels:
                self.canvas.delete(pixel_id)
        self.pixels.clear() 

        for y_px in range(self.HEIGHT_PX):
            row_pixels = []
            for x_px in range(self.WIDTH_PX):
                pixel = self.canvas.create_rectangle(
                    self.start_x + x_px * self.PIXEL_SIZE, self.start_y + y_px * self.PIXEL_SIZE,
                    self.start_x + (x_px + 1) * self.PIXEL_SIZE, self.start_y + (y_px + 1) * self.PIXEL_SIZE,
                    fill=self.INACTIVE_COLOR, outline=''
                )
                row_pixels.append(pixel)
            self.pixels.append(row_pixels)

    def clear(self):
        for y_px in range(self.HEIGHT_PX):
            for x_px in range(self.WIDTH_PX):
                self.set_pixel(x_px, y_px, 0)