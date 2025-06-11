# muserdisplays_gui/base_display_gui.py

import tkinter as tk
from typing import Dict, Tuple

class GUIDisplay:
    """
    Base class for all GUI display simulations.
    Manages the Tkinter canvas and pixel rendering.
    """
    # --- Class Attributes ---
    # These are shared across all instances of GUIDisplay and its subclasses
    PIXEL_SIZE = 2  # Size of each simulated pixel on the Tkinter canvas

    # Default colors (can be overridden by subclasses)
    BACKGROUND_COLOR = "gray"
    ACTIVE_COLOR = "red"
    # --- End Class Attributes ---

    def __init__(self, canvas: tk.Canvas, start_x: int = 0, start_y: int = 0):
        self.canvas = canvas
        self.start_x = start_x
        self.start_y = start_y
        self.pixels: Dict[Tuple[int, int], int] = {} # Stores (x,y) -> canvas_item_id

    def _draw_pixel(self, x_px: int, y_px: int, color: str):
        """Draws a single pixel rectangle on the canvas."""
        x1 = self.start_x + x_px * self.PIXEL_SIZE
        y1 = self.start_y + y_px * self.PIXEL_SIZE
        x2 = x1 + self.PIXEL_SIZE
        y2 = y1 + self.PIXEL_SIZE
        pixel_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        self.pixels[(x_px, y_px)] = pixel_id

    def _update_pixel(self, x_px: int, y_px: int, color: str):
        """Updates the color of an existing pixel or draws a new one."""
        pixel_key = (x_px, y_px)
        if pixel_key in self.pixels:
            self.canvas.itemconfig(self.pixels[pixel_key], fill=color)
        else:
            self._draw_pixel(x_px, y_px, color)

    def clear(self):
        """Clears all active pixels on the display, setting them to background color."""
        for pixel_id in self.pixels.values():
            self.canvas.delete(pixel_id)
        self.pixels.clear()
        # Note: If clear should truly revert to an "empty" state,
        # you might call self.render_empty_display() here.
        # However, typically clear just turns off pixels, and render_empty_display
        # sets up the initial background.

    def render_empty_display(self):
        """
        Subclasses must implement this to draw the initial background
        of their specific display type.
        """
        raise NotImplementedError("Subclasses must implement render_empty_display()")

    def render(self):
        """
        Subclasses must implement this to render their current state.
        This method will vary greatly depending on the display type.
        """
        raise NotImplementedError("Subclasses must implement render()")