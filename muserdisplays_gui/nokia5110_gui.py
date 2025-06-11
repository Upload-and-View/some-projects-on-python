# /home/muser/Desktop/proeject/muserdisplays_gui/nokia5110_gui.py

import tkinter as tk
from .base_display_gui import GUIDisplay
from .fonts import FONT_5X7 

class Nokia5110_GUI(GUIDisplay):
    """
    A GUI simulation of a Nokia 5110 (PCD8544) LCD display.
    """
    WIDTH_PX = 84   # Total width of the display in logical pixels
    HEIGHT_PX = 48  # Total height of the display in logical pixels

    CHAR_WIDTH_PX = FONT_5X7["CHAR_WIDTH_PX"]    # Width of a single character in pixels (for FONT_5X7)
    CHAR_HEIGHT_PX = FONT_5X7["CHAR_HEIGHT_PX"]   # Height of a single character in pixels (for FONT_5X7)
    LINE_SPACING_PX = 1  # 1 pixel vertical spacing between character lines for Nokia 5110

    # Effective height per line including spacing: CHAR_HEIGHT_PX + LINE_SPACING_PX
    EFFECTIVE_LINE_HEIGHT_PX = CHAR_HEIGHT_PX + LINE_SPACING_PX

    NUM_LINES = HEIGHT_PX // EFFECTIVE_LINE_HEIGHT_PX 
    CHARS_PER_LINE = WIDTH_PX // CHAR_WIDTH_PX 

    # Override default colors
    BACKGROUND_COLOR = "darkgreen" 
    ACTIVE_COLOR = "black"         

    def __init__(self, canvas: tk.Canvas, start_x: int = 0, start_y: int = 0):
        super().__init__(canvas, start_x, start_y)
        self.font = FONT_5X7
        self.pixel_buffer = [[0 for _ in range(self.WIDTH_PX)] for _ in range(self.HEIGHT_PX)]
        self.pixels = [] 
        self.PIXEL_SIZE = 2 # Added scaling factor for Nokia 5110 display

        self.render_empty_display() 

    def _update_pixel(self, x_px: int, y_px: int, color: str):
        """Internal method to update the color of a specific pixel on the canvas."""
        if 0 <= x_px < self.WIDTH_PX and 0 <= y_px < self.HEIGHT_PX:
            self.canvas.itemconfig(self.pixels[y_px][x_px], fill=color)

    def _draw_char(self, x_char: int, y_line: int, char: str):
        """
        Draws a single character's bitmap directly into the pixel buffer
        at a character grid position.
        """
        char_bitmap = self.font.get(char.upper(), self.font[' '])

        start_x_px = x_char * self.CHAR_WIDTH_PX
        start_y_px = y_line * self.EFFECTIVE_LINE_HEIGHT_PX

        for y_offset in range(self.CHAR_HEIGHT_PX):
            for x_offset in range(self.CHAR_WIDTH_PX):
                bitmap_idx = y_offset * self.CHAR_WIDTH_PX + x_offset
                is_pixel_active = (bitmap_idx < len(char_bitmap) and char_bitmap[bitmap_idx] == '1')
                
                self.set_pixel(start_x_px + x_offset, start_y_px + y_offset, is_pixel_active)

    def write_text(self, x_char: int, y_line: int, text: str):
        """
        Writes text starting at a specific character column (x_char) and line (y_line).
        Text will wrap to the next line if it exceeds CHARS_PER_LINE.
        Text will be truncated if it exceeds the display's total lines.
        """
        current_x = x_char
        current_y = y_line

        for char in text:
            if current_x >= self.CHARS_PER_LINE:
                current_x = 0
                current_y += 1
            
            if current_y >= self.NUM_LINES:
                break 

            self._draw_char(current_x, current_y, char)
            current_x += 1

    def set_pixel(self, x: int, y: int, on: bool):
        """Sets an individual pixel on/off."""
        if 0 <= x < self.WIDTH_PX and 0 <= y < self.HEIGHT_PX:
            self.pixel_buffer[y][x] = 1 if on else 0
            color = self.ACTIVE_COLOR if on else self.BACKGROUND_COLOR
            self._update_pixel(x, y, color)

    def clear_line(self, line_num: int):
        """Clears a specific text line."""
        if 0 <= line_num < self.NUM_LINES:
            start_px_y = line_num * self.EFFECTIVE_LINE_HEIGHT_PX
            for y_px in range(start_px_y, start_px_y + self.EFFECTIVE_LINE_HEIGHT_PX):
                for x_px in range(self.WIDTH_PX):
                    self.set_pixel(x_px, y_px, False) 

    def clear(self):
        """Clears the entire display, turning off all pixels."""
        for y_px in range(self.HEIGHT_PX):
            for x_px in range(self.WIDTH_PX):
                self.set_pixel(x_px, y_px, False)

    def render_empty_display(self):
        """
        Renders the initial empty display by creating all pixel rectangles
        on the canvas with the background color.
        """
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
                    fill=self.BACKGROUND_COLOR, outline='' 
                )
                row_pixels.append(pixel)
            self.pixels.append(row_pixels)