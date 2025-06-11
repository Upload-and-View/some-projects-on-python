# /home/muser/Desktop/proeject/muserdisplays_gui/seven_segment_gui.py

import tkinter as tk
from .base_display_gui import GUIDisplay
from typing import Dict, List, Tuple

class SevenSegmentDisplayGUI(GUIDisplay):
    """
    A GUI simulation of a single seven-segment display.
    Each segment is a rectangle.
    """
    SEGMENT_MAP: Dict[str, List[str]] = {
        '0': ['a', 'b', 'c', 'd', 'e', 'f'],
        '1': ['b', 'c'],
        '2': ['a', 'b', 'd', 'e', 'g'],
        '3': ['a', 'b', 'c', 'd', 'g'],
        '4': ['f', 'g', 'b', 'c'],
        '5': ['a', 'c', 'd', 'f', 'g'],
        '6': ['a', 'c', 'd', 'e', 'f', 'g'],
        '7': ['a', 'b', 'c'],
        '8': ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
        '9': ['a', 'b', 'c', 'd', 'f', 'g'],
        'A': ['a', 'b', 'c', 'e', 'f', 'g'], 
        'B': ['c', 'd', 'e', 'f', 'g'],     
        'C': ['a', 'd', 'e', 'f'],         
        'D': ['b', 'c', 'd', 'e', 'g'],     
        'E': ['a', 'd', 'e', 'f', 'g'],     
        'F': ['a', 'e', 'f', 'g'],         
        ' ': [],                           
        '-': ['g']                         
    }

    SEGMENT_WIDTH_RATIO = 0.2
    SEGMENT_LENGTH_RATIO = 0.8
    DISPLAY_SCALE = 50 

    ACTIVE_COLOR = "red"
    INACTIVE_COLOR = "darkred"
    BACKGROUND_COLOR = "black"

    def __init__(self, canvas: tk.Canvas, start_x: int = 0, start_y: int = 0):
        super().__init__(canvas, start_x, start_y)
        self.segment_ids: Dict[str, int] = {}
        self.draw_segments()

    def _get_segment_coords(self, segment_name: str) -> Tuple[int, int, int, int]:
        """Calculates coordinates for each segment based on segment name."""
        scale = self.DISPLAY_SCALE
        w = self.SEGMENT_WIDTH_RATIO * scale 
        l = self.SEGMENT_LENGTH_RATIO * scale 

        coords_map = {
            'a': (w, 0, l + w, w),             
            'b': (l + w, w, l + w + w, l + w), 
            'c': (l + w, l + w + w, l + w + w, 2 * l + w), 
            'd': (w, 2 * l + 2 * w, l + w, 2 * l + 2 * w + w), 
            'e': (0, l + w + w, w, 2 * l + w), 
            'f': (0, w, w, l + w),             
            'g': (w, l + w, l + w, l + w + w), 
            'dp': (2 * l + 2 * w, 2 * l + 2 * w, 2 * l + 2 * w + w, 2 * l + 2 * w + w) 
        }

        x1, y1, x2, y2 = coords_map.get(segment_name, (0,0,0,0))
        x1_abs = self.start_x + x1
        y1_abs = self.start_y + y1
        x2_abs = self.start_x + x2
        y2_abs = self.start_y + y2
        return (x1_abs, y1_abs, x2_abs, y2_abs)

    def draw_segments(self):
        """Draws all segments as inactive initially."""
        for segment_name in self.SEGMENT_MAP.keys():
            coords = self._get_segment_coords(segment_name)
            if coords != (0,0,0,0): 
                segment_id = self.canvas.create_rectangle(
                    coords[0], coords[1], coords[2], coords[3],
                    fill=self.INACTIVE_COLOR, outline=self.INACTIVE_COLOR
                )
                self.segment_ids[segment_name] = segment_id

    def show_digit(self, digit: str, dp_on: bool = False):
        """
        Displays a digit on the seven-segment display.
        Args:
            digit (str): The digit to display ('0'-'9', 'A'-'F', or ' ').
            dp_on (bool): Whether the decimal point should be on.
        """
        digit = digit.upper()
        segments_to_light = self.SEGMENT_MAP.get(digit, [])

        for segment_name, segment_id in self.segment_ids.items():
            if segment_name == 'dp':
                color = self.ACTIVE_COLOR if dp_on else self.INACTIVE_COLOR
            elif segment_name in segments_to_light:
                color = self.ACTIVE_COLOR
            else:
                color = self.INACTIVE_COLOR
            self.canvas.itemconfig(segment_id, fill=color, outline=color)

    def clear(self):
        """Turns off all segments."""
        self.show_digit(' ', dp_on=False) 

    def render(self):
        pass