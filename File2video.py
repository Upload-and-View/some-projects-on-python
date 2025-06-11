import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import os
import threading

class DataToVideoConverterWithBinaryFileThreadedEnhancedColors:
    def __init__(self, master):
        self.master = master
        master.title("Text/Binary to Video Converter")

        self.input_label = tk.Label(master, text="Enter Text (or space-separated binary):")
        self.input_label.pack(pady=5)

        self.input_text = tk.Text(master, height=5, width=40)
        self.input_text.pack(padx=10, pady=5)

        self.data_type_label = tk.Label(master, text="Input Type:")
        self.data_type_label.pack(pady=5)

        self.data_type = tk.StringVar(master)
        self.data_type.set("text")  # Default value
        self.data_type_options = ["text", "binary", "binary file"]
        self.data_type_menu = tk.OptionMenu(master, self.data_type, *self.data_type_options)
        self.data_type_menu.pack(padx=10, pady=5)

        self.binary_file_path = tk.StringVar()
        self.binary_file_path.set("Not selected")
        self.browse_binary_button = tk.Button(master, text="Browse Binary File", command=self.browse_binary)
        self.browse_binary_button.pack(pady=5)
        self.binary_file_label = tk.Label(master, textvariable=self.binary_file_path)
        self.binary_file_label.pack(pady=5)
        self.update_binary_file_widgets() # Initial state

        self.output_path = tk.StringVar()
        self.output_path.set("Not selected")
        self.browse_output_button = tk.Button(master, text="Browse Output Path", command=self.browse_output)
        self.browse_output_button.pack(pady=5)
        self.output_label = tk.Label(master, textvariable=self.output_path)
        self.output_label.pack(pady=5)

        self.convert_button = tk.Button(master, text="Convert to Video", command=self.start_conversion_thread)
        self.convert_button.pack(pady=10)

        self.status_label = tk.Label(master, text="Ready")
        self.status_label.pack(pady=5)

        self.data_type.trace_add("write", self.update_binary_file_widgets)

    def update_binary_file_widgets(self, *args):
        if self.data_type.get() == "binary file":
            self.browse_binary_button.pack(pady=5)
            self.binary_file_label.pack(pady=5)
            self.input_label.config(text="Select Binary File:")
            self.input_text.pack_forget()
        else:
            self.browse_binary_button.pack_forget()
            self.binary_file_label.pack_forget()
            self.input_label.config(text="Enter Text (or space-separated binary):")
            self.input_text.pack(padx=10, pady=5)

    def browse_binary(self):
        filepath = filedialog.askopenfilename(
            title="Select Binary File",
            filetypes=[("Binary files", "*.*"), ("All files", "*.*")]
        )
        if filepath:
            self.binary_file_path.set(filepath)

    def browse_output(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".avi",
            filetypes=[("AVI files", "*.avi"), ("All files", "*.*")]
        )
        if filepath:
            self.output_path.set(filepath)

    def start_conversion_thread(self):
        data_type = self.data_type.get()
        output_file = self.output_path.get()

        if output_file == "Not selected":
            self.status_label.config(text="Please select an output path.")
            return

        self.status_label.config(text="Starting conversion...")
        threading.Thread(target=self.convert_data_to_video, args=(data_type, output_file)).start()

    def convert_data_to_video(self, data_type, output_file):
        try:
            if data_type == "text":
                input_data = self.input_text.get("1.0", tk.END).strip()
                data_bytes = input_data.encode('utf-8')
                self.encode_bytes_to_video(data_bytes, output_file)
                self.master.after(0, self.status_label.config, {"text": f"Text converted successfully! Video saved to {output_file}"})
            elif data_type == "binary":
                input_data = self.input_text.get("1.0", tk.END).strip()
                binary_strings = input_data.split()
                data_bytes = bytes([int(b, 2) for b in binary_strings])
                self.encode_bytes_to_video(data_bytes, output_file)
                self.master.after(0, self.status_label.config, {"text": f"Binary text converted successfully! Video saved to {output_file}"})
            elif data_type == "binary file":
                binary_file = self.binary_file_path.get()
                if binary_file == "Not selected":
                    self.master.after(0, self.status_label.config, {"text": "Please select a binary file."})
                    return
                with open(binary_file, 'rb') as f:
                    data_bytes = f.read()
                self.encode_bytes_to_video(data_bytes, output_file)
                self.master.after(0, self.status_label.config, {"text": f"Binary file converted successfully! Video saved to {output_file}"})

        except Exception as e:
            self.master.after(0, self.status_label.config, {"text": f"Conversion failed: {e}"})

    def encode_bytes_to_video(self, data_bytes, output_file):
        frame_width = 256
        frame_height = 256
        fps = 60
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_file, fourcc, fps, (frame_width, frame_height), isColor=True)

        num_squares_per_row = 64
        square_size = frame_width // num_squares_per_row  # 256 / 64 = 4 pixels
        bytes_per_frame = (num_squares_per_row * num_squares_per_row) // 8

        for i in range(0, len(data_bytes), bytes_per_frame):
            frame_bytes = data_bytes[i:i + bytes_per_frame]
            frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

            bit_index = 0
            for byte_val in frame_bytes:
                binary_representation = format(byte_val, '08b')
                for bit in binary_representation:
                    row = bit_index // num_squares_per_row
                    col = bit_index % num_squares_per_row
                    start_x = col * square_size
                    end_x = start_x + square_size
                    start_y = row * square_size
                    end_y = start_y + square_size
                    color = (0, 255, 0) if bit == '1' else (0, 0, 255)
                    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), color, -1)
                    bit_index += 1

                    if bit_index >= num_squares_per_row * num_squares_per_row:
                        break
                if bit_index >= num_squares_per_row * num_squares_per_row:
                    break

            out.write(frame)

        out.release()

if __name__ == "__main__":
    root = tk.Tk()
    converter = DataToVideoConverterWithBinaryFileThreadedEnhancedColors(root)
    root.mainloop()