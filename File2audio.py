import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import threading
import wave
import struct

class DataToAudioFileConverter:
    def __init__(self, master):
        self.master = master
        master.title("Data to Audio File Converter")

        self.input_label = tk.Label(master, text="Enter Data:")
        self.input_label.pack(pady=5)

        self.input_text = tk.Text(master, height=5, width=40)
        self.input_text.pack(padx=10, pady=5)

        self.input_type_label = tk.Label(master, text="Input Type:")
        self.input_type_label.pack(pady=5)

        self.input_type = tk.StringVar(master)
        self.input_type.set("binary_numbers")  # Default value
        self.input_type_options = ["binary_numbers", "text", "binary_file"]
        self.input_type_menu = tk.OptionMenu(master, self.input_type, *self.input_type_options, command=self.update_input_widgets)
        self.input_type_menu.pack(padx=10, pady=5)

        self.binary_file_path = tk.StringVar()
        self.binary_file_path.set("Not selected")
        self.browse_binary_button = tk.Button(master, text="Browse Binary File", command=self.browse_binary)
        self.browse_binary_button.pack(pady=5)
        self.binary_file_label = tk.Label(master, textvariable=self.binary_file_path)
        self.binary_file_label.pack(pady=5)

        self.output_path = tk.StringVar()
        self.output_path.set("Not selected")
        self.browse_output_button = tk.Button(master, text="Browse Output Path", command=self.browse_output)
        self.browse_output_button.pack(pady=5)
        self.output_label = tk.Label(master, textvariable=self.output_path)
        self.output_label.pack(pady=5)

        self.update_input_widgets(self.input_type.get()) # Initial setup

        self.convert_button = tk.Button(master, text="Convert to Audio File", command=self.start_conversion_thread)
        self.convert_button.pack(pady=10)

        self.status_label = tk.Label(master, text="Ready")
        self.status_label.pack(pady=5)

    def update_input_widgets(self, input_type):
        if input_type == "binary_numbers":
            self.input_label.config(text="Enter space-separated binary numbers:")
            self.input_text.pack(padx=10, pady=5)
            self.browse_binary_button.pack_forget()
            self.binary_file_label.pack_forget()
        elif input_type == "text":
            self.input_label.config(text="Enter text:")
            self.input_text.pack(padx=10, pady=5)
            self.browse_binary_button.pack_forget()
            self.binary_file_label.pack_forget()
        elif input_type == "binary_file":
            self.input_label.config(text="Select Binary File:")
            self.input_text.pack_forget()
            self.browse_binary_button.pack(pady=5)
            self.binary_file_label.pack(pady=5)

    def browse_binary(self):
        filepath = filedialog.askopenfilename(
            title="Select Binary File",
            filetypes=[("Binary files", "*.*"), ("All files", "*.*")]
        )
        if filepath:
            self.binary_file_path.set(filepath)

    def browse_output(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if filepath:
            self.output_path.set(filepath)

    def start_conversion_thread(self):
        input_data = self.input_text.get("1.0", tk.END).strip()
        input_type = self.input_type.get()
        binary_file_path = self.binary_file_path.get()
        output_file = self.output_path.get()

        if output_file == "Not selected":
            self.status_label.config(text="Please select an output path.")
            return

        self.status_label.config(text="Preparing audio file...")
        threading.Thread(target=self.convert_to_audio_file, args=(input_data, input_type, binary_file_path, output_file)).start()

    def convert_to_audio_file(self, input_data, input_type, binary_file_path, output_file):
        try:
            all_binary_data = []

            if input_type == "binary_numbers":
                all_binary_data = input_data.split()
            elif input_type == "text":
                encoded_bytes = input_data.encode('utf-8')
                all_binary_data = [format(byte, '08b') for byte in encoded_bytes]
            elif input_type == "binary_file":
                if binary_file_path == "Not selected":
                    self.master.after(0, self.status_label.config, {"text": "Please select a binary file."})
                    return
                with open(binary_file_path, 'rb') as f:
                    byte_data = f.read()
                all_binary_data = [format(byte, '08b') for byte in byte_data]

            sample_rate = 44100
            duration = 0.1  # seconds
            frequency_map = {
                '0': 220,  # A3
                '1': 440   # A4
            }
            num_channels = 1
            bytes_per_sample = 2  # 16-bit audio

            audio_data = []
            for binary_str in all_binary_data:
                for bit in binary_str:
                    frequency = frequency_map.get(bit, 0)
                    if frequency > 0:
                        t = np.linspace(0, duration, int(sample_rate * duration), False)
                        note = np.sin(2 * np.pi * frequency * t)
                        normalized_note = note * (2**15 - 1) / np.max(np.abs(note))
                        audio_data.extend(normalized_note.astype(np.int16).tobytes())
                    else:
                        # Add silence for unrecognized bits
                        silent_frame = np.zeros(int(sample_rate * duration), dtype=np.int16).tobytes()
                        audio_data.extend(silent_frame)

            with wave.open(output_file, 'w') as wf:
                wf.setnchannels(num_channels)
                wf.setsampwidth(bytes_per_sample)
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(audio_data))

            self.master.after(0, self.status_label.config, {"text": f"Audio file saved to {output_file}"})

        except Exception as e:
            self.master.after(0, self.status_label.config, {"text": f"Audio file creation error: {e}"})

if __name__ == "__main__":
    root = tk.Tk()
    converter = DataToAudioFileConverter(root)
    root.mainloop()