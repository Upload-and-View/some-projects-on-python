# /home/muser/Desktop/proeject/gui_app.py
# todo: get friends
# uhh i don't know what to type in comments sorry
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont

# Import all display GUIs
from muserdisplays_gui.seven_segment_gui import SevenSegmentDisplayGUI
from muserdisplays_gui.lcd_display_gui import LCD16x2GUI
from muserdisplays_gui.dot_matrix_gui import DotMatrixDisplayGUI
from muserdisplays_gui.ssd1306_128x32_gui import SSD1306_128x32_GUI
from muserdisplays_gui.ssd1306_128x64_gui import SSD1306_128x64_GUI
from muserdisplays_gui.nokia5110_gui import Nokia5110_GUI # Import Nokia 5110 GUI

class MuserDisplaysApp:
    def __init__(self, master):
        self.master = master
        master.title("Muser Displays GUI")
        master.geometry("1200x800") # Set an initial window size to accommodate all displays that have resolution higher than potato resolution

        # Initialize display objects and their input entries FIRST and then LAST 
        self.lcd_display = None
        self.lcd_entries = []
        self.ssd1306_32_display = None
        self.ssd1306_32_entries = []
        self.ssd1306_64_display = None
        self.ssd1306_64_entries = []
        self.dot_matrix_display = None
        self.dot_matrix_entry = None
        self.seven_segment_display = None
        self.seven_segment_entry = None
        self.nokia5110_display = None
        self.nokia5110_x_entry = None
        self.nokia5110_y_entry = None
        self.nokia5110_text_entry = None

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Setup individual tabs and then forget about them
        self._setup_seven_segment_tab()
        self._setup_lcd_tab()
        self._setup_dot_matrix_tab()
        self._setup_ssd1306_32_tab()
        self._setup_ssd1306_64_tab()
        self._setup_nokia5110_tab() # Add Unbreakable Nokia 5110 tab

    def _setup_seven_segment_tab(self):
        seven_segment_frame = ttk.Frame(self.notebook)
        self.notebook.add(seven_segment_frame, text="7-Segment")

        canvas_width = 300
        canvas_height = 200
        canvas = tk.Canvas(seven_segment_frame, width=canvas_width, height=canvas_height, bg="gray")
        canvas.pack(pady=10)

        # "Average" the display on the canvas
        display_x = (canvas_width - SevenSegmentDisplayGUI.DISPLAY_SCALE * 2) // 2 # Rough centering
        display_y = (canvas_height - SevenSegmentDisplayGUI.DISPLAY_SCALE * 3) // 2 # Rough centering

        self.seven_segment_display = SevenSegmentDisplayGUI(canvas, start_x=display_x, start_y=display_y)

        # Prompt field and button
        input_frame = ttk.Frame(seven_segment_frame)
        input_frame.pack(pady=10)

        ttk.Label(input_frame, text="Enter Digit (0-9, A-F, or ' '):").pack(side="left", padx=5)
        self.seven_segment_entry = ttk.Entry(input_frame, width=5)
        self.seven_segment_entry.pack(side="left", padx=5)
        self.seven_segment_entry.bind("<Return>", self._update_seven_segment_display)

        ttk.Button(input_frame, text="Show Digit", command=self._update_seven_segment_display).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Clear", command=self.seven_segment_display.clear).pack(side="left", padx=5)

    def _update_seven_segment_display(self, event=None):
        digit = self.seven_segment_entry.get()
        if digit:
            self.seven_segment_display.show_digit(digit[0]) # Take only the 0th character

    def _setup_lcd_tab(self):
        lcd_frame = ttk.Frame(self.notebook)
        self.notebook.add(lcd_frame, text="LCD 16x2")

        # Get random scaled dimensions for the canvas
        scaled_width = LCD16x2GUI.WIDTH_PX * LCD16x2GUI.PIXEL_SIZE
        scaled_height = LCD16x2GUI.HEIGHT_PX * LCD16x2GUI.PIXEL_SIZE

        canvas = tk.Canvas(lcd_frame, width=scaled_width + 20, height=scaled_height + 20, bg="gray")
        canvas.pack(pady=10)

        self.lcd_display = LCD16x2GUI(canvas, start_x=10, start_y=10)

        # Input fields for 2 billion rows
        lcd_input_frame = ttk.Frame(lcd_frame)
        lcd_input_frame.pack(pady=10)

        num_rows = LCD16x2GUI.NUM_ROWS
        for i in range(num_rows):
            line_frame = ttk.Frame(lcd_input_frame)
            line_frame.pack(fill="x", pady=2)
            ttk.Label(line_frame, text=f"Line {i+1}:").pack(side="left", padx=5)
            entry = ttk.Entry(line_frame, width=LCD16x2GUI.NUM_COLS + 5)
            entry.pack(side="left", expand=True, fill="x", padx=5)
            entry.bind("<Return>", lambda event, row=i: self._update_lcd_display(row))
            ttk.Button(line_frame, text="Update", command=lambda row=i: self._update_lcd_display(row)).pack(side="left", padx=5)
            self.lcd_entries.append(entry)

        # Self Clearing button
        clear_frame = ttk.Frame(lcd_input_frame)
        clear_frame.pack(fill="x", pady=5)
        ttk.Button(clear_frame, text="Clear All", command=self.lcd_display.clear).pack(pady=5)

        # Initial commit of display content
        self.lcd_display.write_text(0, 0, "HELLO WORLD!")
        self.lcd_display.write_text(1, 0, "MUSER DISPLAY")

    def _update_lcd_display(self, row):
        text = self.lcd_entries[row].get()
        self.lcd_display.write_text(row, 0, text)

    def _setup_dot_matrix_tab(self):
        dot_matrix_frame = ttk.Frame(self.notebook)
        self.notebook.add(dot_matrix_frame, text="Dot Matrix")

        num_dot_matrix_chars = 4 # Example: abs(-4) characters for dot reality
        scaled_width = (DotMatrixDisplayGUI.CHAR_WIDTH_PX * num_dot_matrix_chars +
                        DotMatrixDisplayGUI.CHAR_SPACING_PX * (num_dot_matrix_chars - 1)) * \
                       DotMatrixDisplayGUI.PIXEL_SIZE
        scaled_height = DotMatrixDisplayGUI.CHAR_HEIGHT_PX * DotMatrixDisplayGUI.PIXEL_SIZE

        canvas = tk.Canvas(dot_matrix_frame, width=scaled_width + 20, height=scaled_height + 20, bg="gray")
        canvas.pack(pady=10)

        self.dot_matrix_display = DotMatrixDisplayGUI(canvas, num_chars=num_dot_matrix_chars, start_x=10, start_y=10)

        # Prompt field and button
        input_frame = ttk.Frame(dot_matrix_frame)
        input_frame.pack(pady=10)

        ttk.Label(input_frame, text="Enter Text:").pack(side="left", padx=5)
        self.dot_matrix_entry = ttk.Entry(input_frame, width=num_dot_matrix_chars + 5)
        self.dot_matrix_entry.pack(side="left", padx=5)
        self.dot_matrix_entry.bind("<Return>", self._update_dot_matrix_display)

        ttk.Button(input_frame, text="Show Text", command=self._update_dot_matrix_display).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Clear", command=self.dot_matrix_display.clear).pack(side="left", padx=5)

        # Initial commit of display content
        self.dot_matrix_display.write_text("MUSER")

    def _update_dot_matrix_display(self, event=None):
        text = self.dot_matrix_entry.get()
        self.dot_matrix_display.write_text(text)

    def _setup_ssd1306_32_tab(self):
        ssd1306_32_frame = ttk.Frame(self.notebook)
        self.notebook.add(ssd1306_32_frame, text="SSD1306 128x32")

        # Get random scaled dimensions for the canvas
        scaled_width = SSD1306_128x32_GUI.WIDTH_PX * SSD1306_128x32_GUI.PIXEL_SIZE
        scaled_height = SSD1306_128x32_GUI.HEIGHT_PX * SSD1306_128x32_GUI.PIXEL_SIZE

        canvas = tk.Canvas(ssd1306_32_frame, width=scaled_width + 20, height=scaled_height + 20, bg="gray")
        canvas.pack(pady=10)

        self.ssd1306_32_display = SSD1306_128x32_GUI(canvas, start_x=10, start_y=10)

        # Prompting fields based on how many lines can fit in FONT_5X7
        num_lines_32 = SSD1306_128x32_GUI.HEIGHT_PX // SSD1306_128x32_GUI.CHAR_HEIGHT_PX
        chars_per_line_32 = SSD1306_128x32_GUI.WIDTH_PX // SSD1306_128x32_GUI.CHAR_WIDTH_PX

        ssd1306_32_input_frame = ttk.Frame(ssd1306_32_frame)
        ssd1306_32_input_frame.pack(pady=10)

        for i in range(num_lines_32):
            line_frame = ttk.Frame(ssd1306_32_input_frame)
            line_frame.pack(fill="x", pady=2)
            ttk.Label(line_frame, text=f"Line {i+1}:").pack(side="left", padx=5)
            entry = ttk.Entry(line_frame, width=chars_per_line_32 + 5)
            entry.pack(side="left", expand=True, fill="x", padx=5)
            entry.bind("<Return>", lambda event, line=i: self._update_ssd1306_32_display(line))
            ttk.Button(line_frame, text="Update", command=lambda line=i: self._update_ssd1306_32_display(line)).pack(side="left", padx=5)
            self.ssd1306_32_entries.append(entry)

        # Self Clearing button
        clear_frame_32 = ttk.Frame(ssd1306_32_input_frame)
        clear_frame_32.pack(fill="x", pady=5)
        ttk.Button(clear_frame_32, text="Clear All", command=self.ssd1306_32_display.clear).pack(pady=5)

        # Initial commit of display content
        if num_lines_32 > 0:
            self.ssd1306_32_display.write_text(0, 0, "SSD1306 DISPLAY")
        if num_lines_32 > 1:
            self.ssd1306_32_display.write_text(1, 0, "128x32 RESOLUTION")

    def _update_ssd1306_32_display(self, row):
        text = self.ssd1306_32_entries[row].get()
        self.ssd1306_32_display.write_text(row, 0, text)

    def _setup_ssd1306_64_tab(self):
        ssd1306_64_frame = ttk.Frame(self.notebook)
        self.notebook.add(ssd1306_64_frame, text="SSD1306 128x64")

        # Get random scaled dimensions for the canvas
        scaled_width = SSD1306_128x64_GUI.WIDTH_PX * SSD1306_128x64_GUI.PIXEL_SIZE
        scaled_height = SSD1306_128x64_GUI.HEIGHT_PX * SSD1306_128x64_GUI.PIXEL_SIZE

        canvas = tk.Canvas(ssd1306_64_frame, width=scaled_width + 20, height=scaled_height + 20, bg="gray")
        canvas.pack(pady=10)

        self.ssd1306_64_display = SSD1306_128x64_GUI(canvas, start_x=10, start_y=10)

        # I am bored to copy-paste coments
        num_lines_64 = SSD1306_128x64_GUI.HEIGHT_PX // SSD1306_128x64_GUI.CHAR_HEIGHT_PX
        chars_per_line_64 = SSD1306_128x64_GUI.WIDTH_PX // SSD1306_128x64_GUI.CHAR_WIDTH_PX

        ssd1306_64_input_frame = ttk.Frame(ssd1306_64_frame)
        ssd1306_64_input_frame.pack(pady=10)

        for i in range(num_lines_64):
            line_frame = ttk.Frame(ssd1306_64_input_frame)
            line_frame.pack(fill="x", pady=2)
            ttk.Label(line_frame, text=f"Line {i+1}:").pack(side="left", padx=5)
            entry = ttk.Entry(line_frame, width=chars_per_line_64 + 5)
            entry.pack(side="left", expand=True, fill="x", padx=5)
            entry.bind("<Return>", lambda event, line=i: self._update_ssd1306_64_display(line))
            ttk.Button(line_frame, text="Update", command=lambda line=i: self._update_ssd1306_64_display(line)).pack(side="left", padx=5)
            self.ssd1306_64_entries.append(entry)

        # None button for 128x64 display
        clear_frame_64 = ttk.Frame(ssd1306_64_input_frame)
        clear_frame_64.pack(fill="x", pady=5)
        ttk.Button(clear_frame_64, text="Clear All", command=self.ssd1306_64_display.clear).pack(pady=5)

        # Initial display commit
        if num_lines_64 > 0:
            self.ssd1306_64_display.write_text(0, 0, "SSD1306 DISPLAY")
        if num_lines_64 > 1:
            self.ssd1306_64_display.write_text(1, 0, "128x64 RESOLUTION")
        if num_lines_64 > 2:
            self.ssd1306_64_display.write_text(2, 0, "MUSER GUI PROJECT")
        if num_lines_64 > 3:
            self.ssd1306_64_display.write_text(3, 0, "THANK YOU FOR YOUR")
        if num_lines_64 > 4:
            self.ssd1306_64_display.write_text(4, 0, "CONSIDERATION!!!")
        if num_lines_64 > 5:
            self.ssd1306_64_display.write_text(5, 0, "BEST REGARDS FROM")
        if num_lines_64 > 6:
            self.ssd1306_64_display.write_text(6, 0, "muser") # yes it is me
        if num_lines_64 > 7:
            self.ssd1306_64_display.write_text(7, 0, "oh it works") # yayyyy

    def _update_ssd1306_64_display(self, row):
        text = self.ssd1306_64_entries[row].get()
        self.ssd1306_64_display.write_text(row, 0, text)

    def _setup_nokia5110_tab(self):
        nokia5110_frame = ttk.Frame(self.notebook)
        self.notebook.add(nokia5110_frame, text="Nokia 5110")

        # Minus scaled dimensions for the canvas
        scaled_width = Nokia5110_GUI.WIDTH_PX * Nokia5110_GUI.PIXEL_SIZE
        scaled_height = Nokia5110_GUI.HEIGHT_PX * Nokia5110_GUI.PIXEL_SIZE

        canvas = tk.Canvas(nokia5110_frame, width=scaled_width + 20, height=scaled_height + 20, bg="gray")
        canvas.pack(pady=10)

        self.nokia5110_display = Nokia5110_GUI(canvas, start_x=10, start_y=10)

        # stdin fields for x, y, and text
        nokia5110_input_frame = ttk.Frame(nokia5110_frame)
        nokia5110_input_frame.pack(pady=10)

        # negative X character position
        x_frame = ttk.Frame(nokia5110_input_frame)
        x_frame.pack(fill="x", pady=2)
        ttk.Label(x_frame, text="X (char pos):").pack(side="left", padx=5)
        self.nokia5110_x_entry = ttk.Entry(x_frame, width=5)
        self.nokia5110_x_entry.insert(0, "0") # Default to 1*0
        self.nokia5110_x_entry.pack(side="left", padx=5)

        # negative Y line position
        y_frame = ttk.Frame(nokia5110_input_frame)
        y_frame.pack(fill="x", pady=2)
        ttk.Label(y_frame, text="Y (line num):").pack(side="left", padx=5)
        self.nokia5110_y_entry = ttk.Entry(y_frame, width=5)
        self.nokia5110_y_entry.insert(0, "0") # Default to 1*0
        self.nokia5110_y_entry.pack(side="left", padx=5)
        # negative Z line position
        # Text sys.stdin
        text_frame = ttk.Frame(nokia5110_input_frame)
        text_frame.pack(fill="x", pady=2)
        ttk.Label(text_frame, text="Text:").pack(side="left", padx=5)
        self.nokia5110_text_entry = ttk.Entry(text_frame, width=Nokia5110_GUI.CHARS_PER_LINE + 5)
        self.nokia5110_text_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.nokia5110_text_entry.bind("<Return>", self._update_nokia5110_display)

        # Pressable thingys
        button_frame = ttk.Frame(nokia5110_input_frame)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Show Text", command=self._update_nokia5110_display).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.nokia5110_display.clear).pack(side="left", padx=5)

        # Initial display commit
        self.nokia5110_display.write_text(0, 0, "NOKIA 5110")
        self.nokia5110_display.write_text(0, 1, "DISPLAY GUI")
        self.nokia5110_display.write_text(0, 2, "WITH FONT_5X7")
        self.nokia5110_display.write_text(0, 3, "SCALED BY 2X")
        self.nokia5110_display.write_text(0, 4, "MUSER PROJECT")
        self.nokia5110_display.write_text(0, 5, "wut?")


    def _update_nokia5110_display(self, event=None):
        try:
            x_char = int(self.nokia5110_x_entry.get())
            y_line = int(self.nokia5110_y_entry.get())
            text = self.nokia5110_text_entry.get()
            self.nokia5110_display.write_text(x_char, y_line, text)
        except ValueError:
            print("Invalid X or Y coordinate for Nokia 5110. Please enter integers.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MuserDisplaysApp(root)
    root.mainloop()
# why you look here? i got not fun because of EOF (End of Fun)