# muserdisplays_gui/dot_matrix_gui.py

import tkinter as tk
from .base_display_gui import GUIDisplay
from .fonts import FONT_5X7 # Import the FONT_5X7 dictionary
from typing import List

class DotMatrixDisplayGUI(GUIDisplay):
    """
    A GUI simulation of a single-row dot matrix display.
    """
    # Character dimensions from the font (e.g., FONT_5X7)
    # CORRECTED: Access these as dictionary keys
    CHAR_WIDTH_PX = FONT_5X7["CHAR_WIDTH_PX"]
    CHAR_HEIGHT_PX = FONT_5X7["CHAR_HEIGHT_PX"]

    # Spacing between characters on the dot matrix
    CHAR_SPACING_PX = 1

    # Dot Matrix Colors
    BACKGROUND_COLOR = "black"
    ACTIVE_COLOR = "lime" # Often green for dot matrix displays

    def __init__(self, canvas: tk.Canvas, num_chars: int = 1, start_x: int = 0, start_y: int = 0):
        """
        Initializes the dot matrix GUI display.

        Args:
            canvas: The Tkinter canvas to draw on.
            num_chars: The number of characters the dot matrix can display simultaneously.
            start_x: The X coordinate offset on the canvas for the display's top-left corner.
            start_y: The Y coordinate offset on the canvas for the display's top-left corner.
        """
        super().__init__(canvas, start_x, start_y)
        self.font = FONT_5X7

        self.num_display_chars = num_chars # Number of characters the display can show simultaneously

        # Dynamically calculate the total display width based on the number of characters
        # Each character is CHAR_WIDTH_PX wide, plus CHAR_SPACING_PX between them (except after the last one)
        self.WIDTH_PX = (self.num_display_chars * self.CHAR_WIDTH_PX) + \
                        ((self.num_display_chars - 1) * self.CHAR_SPACING_PX)
        # The height is fixed by the font's character height
        self.HEIGHT_PX = self.CHAR_HEIGHT_PX

        # Internal buffer to hold the characters currently displayed
        self.display_buffer: List[str] = [" "] * self.num_display_chars

        # The initial render() call will be made by gui_app.py after initialization.

    def _draw_char(self, x_char_pos: int, char: str):
        """
        Draws a single character at a specific character position on the dot matrix.
        x_char_pos is the index of the character (0 to num_display_chars-1).
        """
        # Basic bounds check for character position
        if not (0 <= x_char_pos < self.num_display_chars):
            return

        # Get the flattened string bitmap for the character from the font, default to space if not found
        char_bitmap_str = self.font.get(char, self.font[' '])

        # Calculate the starting pixel coordinates for this character on the overall display grid
        # This includes the offset for character spacing
        start_px_x = x_char_pos * (self.CHAR_WIDTH_PX + self.CHAR_SPACING_PX)
        start_px_y = 0 # For a single-row dot matrix, vertical position is always 0

        # Iterate through the pixels of the character's bitmap
        for y_offset in range(self.CHAR_HEIGHT_PX):
            for x_offset in range(self.CHAR_WIDTH_PX):
                # Calculate the index in the flattened string bitmap
                bitmap_idx = y_offset * self.CHAR_WIDTH_PX + x_offset

                is_pixel_on = False
                if 0 <= bitmap_idx < len(char_bitmap_str):
                    is_pixel_on = (char_bitmap_str[bitmap_idx] == '1')

                # Calculate absolute pixel coordinates on the display canvas
                display_x_px = start_px_x + x_offset
                display_y_px = start_px_y + y_offset

                # Ensure pixel is within the actual display boundaries
                if 0 <= display_x_px < self.WIDTH_PX and 0 <= display_y_px < self.HEIGHT_PX:
                    # For dot matrix, 'on' pixels are ACTIVE_COLOR, 'off' are BACKGROUND_COLOR
                    current_color = self.ACTIVE_COLOR if is_pixel_on else self.BACKGROUND_COLOR
                    self._update_pixel(display_x_px, display_y_px, current_color)

    def write_text(self, text: str):
        """
        Writes text to the dot matrix display buffer.
        Text will be truncated if too long, or padded with spaces if too short,
        to fit the number of display characters.
        The display will be re-rendered to show the changes.
        """
        # Ensure text is upper case as fonts are typically defined for uppercase
        text = text.upper()

        # Pad with spaces on the right or truncate to fit the number of display characters
        padded_text = text.ljust(self.num_display_chars, ' ')
        self.display_buffer = list(padded_text[:self.num_display_chars])
        self.render() # Call render to refresh the GUI display

    def clear(self):
        """
        Clears the entire dot matrix display by setting all characters in the buffer to spaces.
        """
        self.write_text(" " * self.num_display_chars) # Use write_text to fill with spaces and re-render

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
        self.pixels.clear() # Clear the dictionary mapping pixel coords to item IDs

    def render(self):
        """
        Renders the current state of the dot matrix display based on its internal `display_buffer`.
        This method fully overrides the `render()` method from `GUIDisplay`.
        """
        # First, ensure the background is drawn and any old pixels are cleared.
        # This effectively "resets" the display visuals before drawing the new state.
        self.render_empty_display()

        # Now, iterate through the display buffer and draw each character
        for char_idx, char in enumerate(self.display_buffer):
            self._draw_char(char_idx, char)