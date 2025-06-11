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
    def __init__(self, host='127.0.0.1', port=12345, client_id=None):
        """
        Initializes the message client optimized for mobile with image support.
        """
        self.host = host
        self.port = port
        self.client_socket = None
        self.client_id = client_id
        self.running = True

        self.root = tk.Tk()
        self.root.title("Mobile Message Client")
        self.root.geometry("400x600")  # Smaller default size for mobile
        self.font = font.Font(family="Arial", size=14) # Slightly larger font
        self.configure_theme()
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.received_image = None

    def configure_theme(self):
        """Configures a simplified dark theme suitable for mobile."""
        bg_color = "#1e1e1e"
        text_color = "#dcdcdc"
        log_bg = "#282828"
        entry_bg = "#303030"
        button_bg = "#4c7899"
        button_fg = text_color
        button_active_bg = "#5e8cb3"

        self.root.configure(bg=bg_color)

        tk_style = tk.ttk.Style()
        tk_style.theme_use('clam') # A more mobile-friendly theme

        tk_style.configure("TLabel", foreground=text_color, background=bg_color, font=self.font)
        tk_style.configure("TEntry", foreground=text_color, background=entry_bg, fieldbackground=entry_bg, bordercolor=entry_bg, font=self.font)
        tk_style.configure("TButton", foreground=button_fg, background=button_bg, relief="flat", bordercolor=button_bg, font=self.font)
        tk_style.map("TButton",
                     foreground=[('active', button_fg)],
                     background=[('active', button_active_bg)])

        self.root.option_add("*ScrolledText*background", log_bg)
        self.root.option_add("*ScrolledText*foreground", text_color)
        self.root.option_add("*ScrolledText*font", self.font)
        self.root.option_add("*Text*background", log_bg)
        self.root.option_add("*Text*foreground", text_color)
        self.root.option_add("*Text*font", self.font)
        self.root.option_add("*Entry*font", self.font)

    def create_widgets(self):
        """Creates the GUI elements, optimized for mobile layout."""
        # --- Top Frame for Connection Setup ---
        self.top_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.top_frame.pack(pady=5, padx=10, fill=tk.X)
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(3, weight=2)
        self.top_frame.grid_columnconfigure(5, weight=1)

        id_row = 0
        host_row = 1
        port_row = 1
        connect_row = 2

        self.id_label = ttk.Label(self.top_frame, text="Your ID:")
        self.id_label.grid(row=id_row, column=0, padx=5, sticky="w")
        self.id_entry = ttk.Entry(self.top_frame)
        self.id_entry.insert(0, self.client_id if self.client_id else "")
        self.id_entry.grid(row=id_row, column=1, padx=5, sticky="ew")
        if self.client_id:
            self.id_entry.config(state=tk.DISABLED)

        self.host_label = ttk.Label(self.top_frame, text="Host:")
        self.host_label.grid(row=host_row, column=0, padx=5, sticky="w")
        self.host_entry = ttk.Entry(self.top_frame, textvariable=tk.StringVar(value=self.host))
        self.host_entry.grid(row=host_row, column=1, padx=5, sticky="ew")

        self.port_label = ttk.Label(self.top_frame, text="Port:")
        self.port_label.grid(row=port_row, column=2, padx=5, sticky="w")
        self.port_entry = ttk.Entry(self.top_frame, width=8, textvariable=tk.StringVar(value=self.port))
        self.port_entry.grid(row=port_row, column=3, padx=5, sticky="ew")

        self.connect_button = ttk.Button(self.top_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=connect_row, column=0, columnspan=4, pady=5, sticky="ew")

        # --- Middle Frame for Log and Image Display ---
        self.middle_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.middle_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        self.middle_frame.grid_rowconfigure(0, weight=1)
        self.middle_frame.grid_rowconfigure(1, weight=0) # Image label
        self.middle_frame.grid_rowconfigure(2, weight=2) # Image canvas
        self.middle_frame.grid_columnconfigure(0, weight=1)

        self.log_label = ttk.Label(self.middle_frame, text="Message Log:")
        self.log_label.grid(row=0, column=0, sticky="ew")
        self.log_text = scrolledtext.ScrolledText(self.middle_frame, wrap=tk.WORD, height=8)
        self.log_text.grid(row=1, column=0, sticky="nsew", pady=(0, 5))
        self.log_text.config(state=tk.DISABLED)

        self.image_label = ttk.Label(self.middle_frame, text="Received Image:")
        self.image_label.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        self.image_canvas = tk.Canvas(self.middle_frame, width=300, height=200, bg="black")
        self.image_canvas.grid(row=3, column=0, sticky="nsew", pady=(0, 5))
        self.displayed_image = None

        # --- Bottom Frame for Message Input and Send Button ---
        self.bottom_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.bottom_frame.pack(pady=5, padx=10, fill=tk.X)
        self.bottom_frame.grid_columnconfigure(1, weight=3)
        self.bottom_frame.grid_columnconfigure(2, weight=1)

        self.target_id_label = ttk.Label(self.bottom_frame, text="To:")
        self.target_id_label.grid(row=0, column=0, padx=5, sticky="w")
        self.target_id_entry = ttk.Entry(self.bottom_frame, width=10)
        self.target_id_entry.grid(row=0, column=1, padx=5, sticky="ew")

        self.message_label = ttk.Label(self.bottom_frame, text="Message:")
        self.message_label.grid(row=1, column=0, padx=5, sticky="w")
        self.message_entry = ttk.Entry(self.bottom_frame)
        self.message_entry.grid(row=1, column=1, padx=5, sticky="ew")

        self.send_button = ttk.Button(self.bottom_frame, text="Send", command=self.send_message, state=tk.DISABLED)
        self.send_button.grid(row=1, column=2, padx=5, sticky="ew")

        self.send_image_button = ttk.Button(self.bottom_frame, text="Send Image", command=self.send_image_dialog, state=tk.DISABLED)
        self.send_image_button.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")

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
                self.update_log(f"Connected as ID: {client_id}")
                self.start_threads()
                self.connect_button.config(state=tk.DISABLED)
                self.send_button.config(state=tk.NORMAL)
                self.send_image_button.config(state=tk.NORMAL)
                self.id_entry.config(state=tk.DISABLED)
                self.host_entry.config(state=tk.DISABLED)
                self.port_entry.config(state=tk.DISABLED)

            elif status_message.get("error"):
                self.update_log(f"Connection error: {status_message['error']}")
                self.client_socket.close()
                self.client_socket = None
            else:
                self.update_log("Failed to connect: Unknown status")
                self.client_socket.close()
                self.client_socket = None

        except Exception as e:
            self.update_log(f"Error connecting: {e}")
            if self.client_socket:
                self.client_socket.close()
            self.client_socket = None

    def receive_messages(self):
        """Receives messages and image info from the server."""
        while self.running and self.client_socket:
            try:
                header_data = self.client_socket.recv(4096)
                if not header_data:
                    break
                try:
                    header = json.loads(header_data.decode('utf-8'))
                    if header.get('type') == 'text' and "content" in header and "sender_id" in header:
                        self.update_log(f"[{header['sender_id']}] {header['content']}")
                    elif header.get('type') == 'image_received' and 'filename' in header:
                        self.update_log(f"Server received image: {header['filename']}")
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
            img.thumbnail((200, 150)) # Smaller thumbnail for mobile
            self.tk_image = ImageTk.PhotoImage(img)
            self.image_canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
            self.image_canvas.delete("all")
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.displayed_image = self.tk_image
        except Exception as e:
            self.update_log(f"Error displaying image: {e}")

    def send_message(self):
        """Sends a text message to the specified target ID."""
        target_id = self.target_id_entry.get()
        message_text = self.message_entry.get()
        sender_id = self.client_id

        if not sender_id or not self.client_socket:
            self.update_log("Connect to server to send message.")
            return
        if not target_id:
            self.update_log("Enter a target ID.")
            return
        if not message_text:
            self.update_log("Enter a message.")
            return

        message = {"type": "text", "target_id": target_id, "content": message_text, "sender_id": sender_id}
        try:
            self.client_socket.send(json.dumps(message).encode('utf-8'))
            self.update_log(f"Sent to {target_id}: {message_text}")
        except socket.error:
            self.update_log("Error sending message.")
            self.disconnect_from_server()
        self.message_entry.delete(0, tk.END)

    def send_image_dialog(self):
        """Opens a file dialog to select an image to send."""
        filepath = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if filepath:
            self.send_image(filepath, self.target_id_entry.get())

    def send_image(self, filepath, target_id):
        """Sends the selected image to the specified target ID."""
        if not self.client_socket:
            self.update_log("Not connected.")
            return
        if not target_id:
            self.update_log("Enter target ID for image.")
            return
        if not self.client_id:
            self.update_log("Client ID not set.")
            return

        try:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)

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
            self.update_log(f"Sending '{filename}' ({filesize} bytes) to {target_id}...")

        except FileNotFoundError:
            self.update_log(f"File not found: {filepath}")
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
    parser = argparse.ArgumentParser(description="Run the Mobile Message Client with Image Support.")
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='The host IP address to connect to.')
    parser.add_argument('--port', type=int, default=12345,
                        help='The port number to connect to.')
    parser.add_argument('--id', type=str, default=None,
                        help='Client ID. If not provided, you will be prompted.')
    args = parser.parse_args()

    client = MessageClient(host=args.host, port=args.port, client_id=args.id)
    client.root.mainloop()