import socket
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext, font, filedialog, Label
import json
import time
import argparse
import os
from PIL import Image, ImageTk
import io

class MessageClient:
    def __init__(self, host='172.20.10.2', port=12345, client_id=None):
        """
        Initializes the message client with image sending and receiving capabilities.
        """
        self.host = host
        self.port = port
        self.client_socket = None
        self.client_id = client_id
        self.running = True

        self.root = tk.Tk()
        self.root.title("Message Client with Image Support")
        self.root.geometry("700x500")
        self.font = font.Font(family="Arial", size=12)
        self.configure_theme()
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.received_image = None # To store the received image data

    def configure_theme(self):
        """Configures the dark theme for the application."""
        self.root.configure(bg="#2d2d2d")
        self.text_color = "#ffffff"
        self.log_bg_color = "#3e3e3e"
        self.entry_bg_color = "#4a4a4a"
        self.button_bg_color = "#4299e1"
        self.button_fg_color = "#ffffff"
        self.button_hover_bg = "#3182ce"

        tk_style = tk.ttk.Style()
        tk_style.configure("TLabel", foreground=self.text_color, background="#2d2d2d")
        tk_style.configure("TEntry", foreground=self.text_color, background=self.entry_bg_color, fieldbackground=self.entry_bg_color, bordercolor=self.entry_bg_color)
        tk_style.configure("TButton", foreground=self.button_fg_color, background=self.button_bg_color, relief="flat", bordercolor=self.button_bg_color)
        tk_style.map("TButton", foreground=[('active', self.button_fg_color)], background=[('active', self.button_hover_bg)])

        self.root.option_add("*TButton*foreground", self.button_fg_color)
        self.root.option_add("*TButton*background", self.button_bg_color)
        self.root.option_add("*TButton*relief", "flat")
        self.root.option_add("*TButton*highlightThickness", 0)

        self.root.option_add("*ScrolledText*background", self.log_bg_color)
        self.root.option_add("*ScrolledText*foreground", self.text_color)
        self.root.option_add("*Text*background", self.log_bg_color)
        self.root.option_add("*Text*foreground", self.text_color)
        self.root.option_add("*Entry*background", self.entry_bg_color)
        self.root.option_add("*Entry*foreground", self.text_color)

    def create_widgets(self):
        """Creates the GUI elements for the client window with image support."""
        # --- Top Frame for Connection Setup ---
        self.top_frame = tk.Frame(self.root, bg="#2d2d2d")
        self.top_frame.pack(pady=10)

        self.id_label = tk.Label(self.top_frame, text="Your ID:", font=self.font, bg="#2d2d2d", fg=self.text_color)
        self.id_label.grid(row=0, column=0, padx=5)
        self.id_entry = tk.Entry(self.top_frame, width=10, font=self.font, bg=self.entry_bg_color, fg=self.text_color)
        self.id_entry.insert(0, self.client_id if self.client_id else "")
        self.id_entry.grid(row=0, column=1, padx=5)
        if self.client_id:
            self.id_entry.config(state=tk.DISABLED)

        self.host_label = tk.Label(self.top_frame, text="Host:", font=self.font, bg="#2d2d2d", fg=self.text_color)
        self.host_label.grid(row=0, column=2, padx=5)
        self.host_entry = tk.Entry(self.top_frame, width=15, font=self.font, textvariable=tk.StringVar(value=self.host), bg=self.entry_bg_color, fg=self.text_color)
        self.host_entry.grid(row=0, column=3, padx=5)

        self.port_label = tk.Label(self.top_frame, text="Port:", font=self.font, bg="#2d2d2d", fg=self.text_color)
        self.port_label.grid(row=0, column=4, padx=5)
        self.port_entry = tk.Entry(self.top_frame, width=10, font=self.font, textvariable=tk.StringVar(value=self.port), bg=self.entry_bg_color, fg=self.text_color)
        self.port_entry.grid(row=0, column=5, padx=5)

        self.connect_button = tk.Button(self.top_frame, text="Connect", command=self.connect_to_server, font=self.font, highlightbackground=self.button_hover_bg, bg=self.button_bg_color, fg=self.button_fg_color, activebackground=self.button_hover_bg, activeforeground=self.button_fg_color)
        self.connect_button.grid(row=1, column=0, columnspan=6, pady=5, sticky="we")

        # --- Middle Frame for Log and Image Display ---
        self.middle_frame = tk.Frame(self.root, bg="#2d2d2d")
        self.middle_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.log_label = tk.Label(self.middle_frame, text="Message Log:", font=self.font, bg="#2d2d2d", fg=self.text_color)
        self.log_label.pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self.middle_frame, wrap=tk.WORD, height=8, font=self.font, bg=self.log_bg_color, fg=self.text_color)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        self.image_label = Label(self.middle_frame, text="Received Image:", font=self.font, bg="#2d2d2d", fg="#aaffaa")
        self.image_label.pack(anchor="w", pady=(5, 0))
        self.image_canvas = tk.Canvas(self.middle_frame, width=300, height=200, bg="black")
        self.image_canvas.pack(fill=tk.X, padx=10)
        self.displayed_image = None

        # --- Bottom Frame for Message Input and Image Sending ---
        self.bottom_frame = tk.Frame(self.root, bg="#2d2d2d")
        self.bottom_frame.pack(pady=10)

        self.target_id_label = tk.Label(self.bottom_frame, text="Target ID:", font=self.font, bg="#2d2d2d", fg=self.text_color)
        self.target_id_label.grid(row=0, column=0, padx=5)
        self.target_id_entry = tk.Entry(self.bottom_frame, width=10, font=self.font, bg=self.entry_bg_color, fg=self.text_color)
        self.target_id_entry.grid(row=0, column=1, padx=5)

        self.message_label = tk.Label(self.bottom_frame, text="Message:", font=self.font, bg="#2d2d2d", fg=self.text_color)
        self.message_label.grid(row=0, column=2, padx=5)
        self.message_entry = tk.Entry(self.bottom_frame, width=30, font=self.font, bg=self.entry_bg_color, fg=self.text_color)
        self.message_entry.grid(row=0, column=3, padx=5)

        self.send_button = tk.Button(self.bottom_frame, text="Send", command=self.send_message, font=self.font, highlightbackground=self.button_hover_bg, bg=self.button_bg_color, fg=self.button_fg_color, activebackground=self.button_hover_bg, activeforeground=self.button_fg_color)
        self.send_button.grid(row=0, column=4, padx=5)
        self.send_button.config(state=tk.DISABLED)

        self.send_image_button = tk.Button(self.bottom_frame, text="Send Image", command=self.send_image_dialog, font=self.font, highlightbackground=self.button_hover_bg, bg=self.button_bg_color, fg=self.button_fg_color, activebackground=self.button_hover_bg, activeforeground=self.button_fg_color)
        self.send_image_button.grid(row=1, column=0, columnspan=5, pady=5, sticky="we")
        self.send_image_button.config(state=tk.DISABLED) # Disable until connected

    def start_threads(self):
        """Starts the message and image receiving threads."""
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def connect_to_server(self):
        """Connects the client to the server."""
        client_id = self.id_entry.get()
        if not client_id:
            self.update_log("Please enter your ID before connecting.")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host_entry.get(), int(self.port_entry.get())))
            self.client_socket.send(json.dumps({"id": client_id}).encode('utf-8'))

            status_data = self.client_socket.recv(1024).decode('utf-8')
            status_message = json.loads(status_data)

            if status_message.get("status") == "connected":
                self.client_id = client_id
                self.update_log(f"Connected to server as ID: {client_id}")
                self.start_threads()
                self.connect_button.config(state=tk.DISABLED)
                self.send_button.config(state=tk.NORMAL)
                self.send_image_button.config(state=tk.NORMAL) # Enable image sending
                self.id_entry.config(state=tk.DISABLED)
                self.host_entry.config(state=tk.DISABLED)
                self.port_entry.config(state=tk.DISABLED)

            elif status_message.get("error"):
                self.update_log(f"Connection error: {status_message['error']}")
                self.client_socket.close()
                self.client_socket = None
            else:
                self.update_log("Failed to connect to server: Unknown status")
                self.client_socket.close()
                self.client_socket = None

        except Exception as e:
            self.update_log(f"Error connecting to server: {e}")
            if self.client_socket:
                self.client_socket.close()
            self.client_socket = None

    def receive_messages(self):
        """Receives messages and image info from the server."""
        while self.running and self.client_socket:
            try:
                header_data = self.client_socket.recv(4096) # Increased buffer for potential headers
                if not header_data:
                    break
                try:
                    header = json.loads(header_data.decode('utf-8'))
                    if header.get('type') == 'text' and "content" in header and "sender_id" in header:
                        self.update_log(f"[{header['sender_id']}] {header['content']}")
                    elif header.get('type') == 'image_received' and 'filename' in header:
                        self.update_log(f"Server received image: {header['filename']}")
                        # Optionally, you could request the image data back from the server if needed for more complex viewing
                    elif header.get('type') == 'image_info' and 'filename' in header and 'size' in header and 'sender_id' in header:
                        filename = header['filename']
                        sender_id = header['sender_id']
                        filesize = header['size']
                        self.receive_image_data(filename, filesize, sender_id)
                    else:
                        self.update_log(f"Received unknown data: {header}")
                except json.JSONDecodeError:
                    self.update_log(f"Received non-JSON data: {header_data.decode('utf-8')}")
            except socket.error:
                self.update_log("Disconnected from server.")
                break
            except Exception as e:
                self.update_log(f"Error receiving data: {e}")
                break
        self.disconnect_from_server()

    def receive_image_data(self, filename, filesize, sender_id):
        """Receives the raw image data from the server."""
        received_bytes = 0
        image_data = b""
        while received_bytes < filesize:
            chunk = self.client_socket.recv(1024)
            if not chunk:
                break
            image_data += chunk
            received_bytes += len(chunk)

        if received_bytes == filesize:
            self.update_log(f"Received image '{filename}' from {sender_id} ({filesize} bytes).")
            self.display_image(image_data)
        else:
            self.update_log(f"Error receiving full image '{filename}' from {sender_id}.")

    def display_image(self, image_data):
        """Displays the received image in the GUI."""
        try:
            img = Image.open(io.BytesIO(image_data))
            img.thumbnail((300, 200))
            self.tk_image = ImageTk.PhotoImage(img)
            self.image_canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
            self.image_canvas.delete("all")
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.displayed_image = self.tk_image
        except Exception as e:
            self.update_log(f"Error displaying received image: {e}")

    def send_message(self):
        """Sends a text message to the specified target ID."""
        target_id = self.target_id_entry.get()
        message_text = self.message_entry.get()
        sender_id = self.client_id

        if not sender_id or not self.client_socket:
            self.update_log("Please connect to a server before sending a message.")
            return
        if not target_id:
            self.update_log("Please enter a target ID.")
            return
        if not message_text:
            self.update_log("Please enter a message.")
            return

        message = {"type": "text", "target_id": target_id, "content": message_text, "sender_id": sender_id}
        try:
            self.client_socket.send(json.dumps(message).encode('utf-8'))
            self.update_log(f"Sent message to {target_id}: {message_text}")
        except socket.error:
            self.update_log("Error sending message.")
            self.disconnect_from_server()
        self.message_entry.delete(0, tk.END)

    def send_image_dialog(self):
        """Opens a file dialog to select an image to send."""
        filepath = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if filepath:
            self.send_image(filepath, self.target_id_entry.get())

    def send_image(self, filepath, target_id):
        """Sends the selected image to the specified target ID."""
        if not self.client_socket:
            self.update_log("Not connected to a server.")
            return
        if not target_id:
            self.update_log("Please enter a target ID to send the image to.")
            return
        if not self.client_id:
            self.update_log("Your client ID is not set.")
            return

        try:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)

            # Send image info header
            header = json.dumps({'type': 'image_info', 'filename': filename, 'size': filesize, 'sender_id': self.client_id}).encode('utf-8')
            self.client_socket.sendall(header)

            with open(filepath, 'rb') as f:
                sent_bytes = 0
                while sent_bytes < filesize:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    self.client_socket.sendall(chunk)
                    sent_bytes += len(chunk)
            self.update_log(f"Sending image '{filename}' ({filesize} bytes) to {target_id}...")

        except FileNotFoundError:
            self.update_log(f"Error: File not found: {filepath}")
        except socket.error as e:
            self.update_log(f"Socket error sending image: {e}")
        except Exception as e:
            self.update_log(f"Error sending image: {e}")

    def update_log(self, message):
        """Updates the log text area with a new message."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def disconnect_from_server(self):
        """Disconnects the client from the server."""
        if self.client_socket:
            try:
                self.client_socket.close()
            except socket.error:
                pass
            self.client_socket = None
            self.update_log("Disconnected from server.")
            self.connect_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.DISABLED)
            self.send_image_button.config(state=tk.DISABLED)
            self.id_entry.config(state=tk.NORMAL)
            self.host_entry.config(state=tk.NORMAL)
            self.port_entry.config(state=tk.NORMAL)

    def on_closing(self):
        """Handles the window closing event."""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except socket.error:
                pass
        self.root.destroy()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Message Client with Image Support.")
    parser.add_argument('--host', type=str, default='192.168.210.33',
                        help='The host IP address to connect to.')
    parser.add_argument('--port', type=int, default=12345,
                        help='The port number to connect to.')
    parser.add_argument('--id', type=str, default=None,
                        help='Client ID. If not provided, you will be prompted.')
    args = parser.parse_args()

    client = MessageClient(host=args.host, port=args.port, client_id=args.id)
    client.root.mainloop()