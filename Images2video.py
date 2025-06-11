import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import cv2
import os
import threading
import time

class ImageToVideoConverter:
    def __init__(self, master):
        self.master = master
        self.master.title("Image to Video Converter")

        self.image_paths = []
        self.image_settings = {}  # {filepath: {'fps': float, 'duration': float}}
        self.output_path = ""
        self.is_converting = False

        self.create_widgets()

    def create_widgets(self):
        # Image List Frame
        self.image_frame = tk.LabelFrame(self.master, text="Selected Images")
        self.image_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.image_list_scrollbar = tk.Scrollbar(self.image_frame)
        self.image_list = tk.Listbox(self.image_frame, yscrollcommand=self.image_list_scrollbar.set, width=60)
        self.image_list_scrollbar.config(command=self.image_list.yview)
        self.image_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.image_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons for Image Management
        self.add_button = tk.Button(self.master, text="Add Images", command=self.add_images)
        self.add_button.pack(pady=5)

        self.select_all_button = tk.Button(self.master, text="Select All", command=self.select_all_images)
        self.select_all_button.pack(pady=5)

        self.edit_button = tk.Button(self.master, text="Edit Settings", state=tk.DISABLED, command=self.edit_multiple_settings)
        self.edit_button.pack(pady=5)

        self.remove_button = tk.Button(self.master, text="Remove Selected", state=tk.DISABLED, command=self.remove_selected)
        self.remove_button.pack(pady=5)

        # Bind events AFTER packing the Listbox
        self.image_list.bind('<<SelectionChanged>>', self.update_button_states)
        # Output Path
        self.output_frame = tk.Frame(self.master)
        self.output_frame.pack(padx=10, pady=5, fill=tk.X)
        tk.Label(self.output_frame, text="Output Video Path:").pack(side=tk.LEFT)
        self.output_path_label = tk.Label(self.output_frame, text="Not selected", anchor="w")
        self.output_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.browse_output_button = tk.Button(self.output_frame, text="Browse", command=self.browse_output_path)
        self.browse_output_button.pack(side=tk.RIGHT)

        # Conversion Button
        self.convert_button = tk.Button(self.master, text="Convert to Video", state=tk.DISABLED, command=self.start_conversion)
        self.convert_button.pack(pady=15)

        # Status Label
        self.status_label = tk.Label(self.master, text="Ready")
        self.status_label.pack(pady=5)
    def select_all_images(self):
        self.image_list.select_set(0, tk.END)
        self.update_button_states(None) # To enable Edit/Remove buttons
    def update_button_states(self, event):
        self.enable_edit_button(event)
        self.enable_remove_button(event)
    def enable_edit_button(self, event):
        print("enable_edit_button function called.")
        if self.image_list.curselection():
            self.edit_button.config(state=tk.NORMAL)
        else:
            self.edit_button.config(state=tk.DISABLED)

    def enable_remove_button(self, event):
        if self.image_list.curselection():
            self.remove_button.config(state=tk.NORMAL)
        else:
            self.remove_button.config(state=tk.DISABLED)

    def add_images(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.gif"), ("All files", "*.*"))
        )
        if filepaths:
            print("Selected filepaths:", filepaths)
            for fp in filepaths:
                print("Processing filepath:", repr(fp))
                if fp not in self.image_paths:
                    self.image_paths.append(fp)
                    filename = os.path.basename(fp)
                    self.image_list.insert(tk.END, filename)
                    self.image_settings[fp] = {'fps': 1.0, 'duration': 1.0}
                    print("Added:", filename)
                else:
                    print("Skipped duplicate:", filename)
            if self.image_paths:
                self.convert_button.config(state=tk.NORMAL)
                self.update_button_states(None) # Update button states after adding
                # Auto-select the first item after adding
                self.image_list.selection_clear(0, tk.END)
                self.image_list.selection_set(0)
                self.image_list.event_generate('<<SelectionChanged>>')


    def edit_settings(self):
        print("Edit Settings button clicked.")
        selected_indices = self.image_list.curselection()
        print("Selected indices in edit_settings:", selected_indices)
        if selected_indices:
            selected_index = selected_indices[0]
            print("Selected index:", selected_index)
            filepath = self.image_paths[selected_index]
            print("Filepath to edit:", filepath)
            settings = self.image_settings[filepath]
            print("Current settings:", settings)

            settings_window = tk.Toplevel(self.master)
            settings_window.title(f"Settings for {os.path.basename(filepath)}")

            tk.Label(settings_window, text="FPS (Frames Per Second):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            fps_entry = tk.Entry(settings_window, width=10)
            fps_entry.insert(0, str(settings['fps']))
            fps_entry.grid(row=0, column=1, padx=5, pady=5)

            tk.Label(settings_window, text="Duration (seconds):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            duration_entry = tk.Entry(settings_window, width=10)
            duration_entry.insert(0, str(settings['duration']))
            duration_entry.grid(row=1, column=1, padx=5, pady=5)
        else:
            print("No image selected to edit.")
    def edit_multiple_settings(self):
        print("Edit Settings button clicked (multiple).")
        selected_indices = self.image_list.curselection()
        print("Selected indices in edit_multiple_settings:", selected_indices)
        if selected_indices:
            settings_window = tk.Toplevel(self.master)
            settings_window.title("Edit Settings for Multiple Images")

            tk.Label(settings_window, text="Apply Duration (seconds) to all selected images:").pack(padx=10, pady=5)
            duration_entry = tk.Entry(settings_window, width=10)
            duration_entry.pack(padx=10, pady=5)

            def apply_duration():
                try:
                    duration = float(duration_entry.get())
                    if duration > 0:
                        for index in selected_indices:
                            filepath = self.image_paths[index]
                            self.image_settings[filepath]['duration'] = duration
                        print("Duration applied to selected images:", duration)
                        settings_window.destroy()
                    else:
                        messagebox.showerror("Error", "Duration must be a positive value.")
                except ValueError:
                    messagebox.showerror("Error", "Invalid input. Please enter a number.")

            apply_button = tk.Button(settings_window, text="Apply to Selected", command=apply_duration)
            apply_button.pack(pady=10)
        else:
            messagebox.showinfo("Info", "Please select one or more images to edit.")
            def save_settings():
                try:
                    fps = float(fps_entry.get())
                    duration = float(duration_entry.get())
                    if fps > 0 and duration > 0:
                        self.image_settings[filepath]['fps'] = fps
                        self.image_settings[filepath]['duration'] = duration
                        settings_window.destroy()
                        print("Settings saved:", self.image_settings[filepath])
                    else:
                        messagebox.showerror("Error", "FPS and Duration must be positive values.")
                except ValueError:
                    messagebox.showerror("Error", "Invalid input. Please enter numbers.")

            save_button = tk.Button(settings_window, text="Save", command=save_settings)
            save_button.grid(row=2, columnspan=2, padx=5, pady=10)

    def remove_selected(self):
        selected_indices = self.image_list.curselection()
        if selected_indices:
            # Iterate in reverse to avoid index issues after removal
            for index in reversed(selected_indices):
                filepath_to_remove = self.image_paths.pop(index)
                self.image_list.delete(index)
                del self.image_settings[filepath_to_remove]
            if not self.image_paths:
                self.convert_button.config(state=tk.DISABLED)
                self.edit_button.config(state=tk.DISABLED)
                self.remove_button.config(state=tk.DISABLED)

    def browse_output_path(self):
        filepath = filedialog.asksaveasfilename(
            title="Save Video As",
            defaultextension=".mp4",
            filetypes=(("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*"))
        )
        if filepath:
            self.output_path = filepath
            self.output_path_label.config(text=self.output_path)
            if self.image_paths:
                self.convert_button.config(state=tk.NORMAL)

    def start_conversion(self):
        if not self.image_paths:
            messagebox.showerror("Error", "Please add images first.")
            return
        if not self.output_path:
            messagebox.showerror("Error", "Please select an output video path.")
            return

        if self.is_converting:
            messagebox.showinfo("Info", "Conversion is already in progress.")
            return

        self.is_converting = True
        self.convert_button.config(state=tk.DISABLED, text="Converting...")
        self.status_label.config(text="Conversion in progress...")

        threading.Thread(target=self.convert_images_to_video).start()

    def convert_images_to_video(self):
        try:
            if not self.image_paths:
                self.master.after(0, self.conversion_complete, "No images selected for conversion.")
                return

            first_image_path = self.image_paths[0]
            try:
                first_image = Image.open(first_image_path)
                frame_width, frame_height = first_image.size
            except Exception as e:
                self.master.after(0, self.conversion_complete, f"Error opening first image: {e}")
                return

            fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Or another codec
            output_path_avi = self.output_path.rsplit('.', 1)[0] + '.avi'
            consistent_fps = 1.0  # Set a consistent FPS for the video (adjust as needed)
            out = cv2.VideoWriter(output_path_avi, fourcc, consistent_fps, (frame_width, frame_height), isColor=True)

            if not out.isOpened():
                self.master.after(0, self.conversion_complete, f"Error: Could not open output video file at {output_path_avi}")
                return

            for img_path in self.image_paths:
                settings = self.image_settings[img_path]
                duration = settings['duration']
                # For a consistent video FPS, the number of frames to add is directly related to the duration
                frames_to_add = int(consistent_fps * duration)

                try:
                    img = cv2.imread(img_path)
                    if img is not None:
                        print(f"Writing image: {img_path} for {duration} seconds ({frames_to_add} frames)")
                        if img.shape[1] != frame_width or img.shape[0] != frame_height:
                            img = cv2.resize(img, (frame_width, frame_height))
                        for _ in range(frames_to_add):
                            out.write(img)
                    else:
                        print(f"Error reading image: {img_path}")
                except Exception as e:
                    print(f"Error processing image {img_path}: {e}")

            out.release()
            self.master.after(0, self.conversion_complete, "Conversion successful!")

        except Exception as e:
            self.master.after(0, self.conversion_complete, f"Conversion failed: {e}")

    def conversion_complete(self, message):
        self.is_converting = False
        self.convert_button.config(state=tk.NORMAL, text="Convert to Video")
        self.status_label.config(text=message)
        if "successful" in message:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    converter = ImageToVideoConverter(root)
    root.mainloop()
