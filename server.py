import socket
import threading
import json
import time
import tkinter as tk
from tkinter import scrolledtext, font

class MessageServer:
    def __init__(self, host='127.0.0.1', port=12345, use_gui=True):
        """
        Initializes the message server.

        Args:
            host (str): The host IP address to bind to.  Defaults to localhost.
            port (int): The port number to listen on. Defaults to 12345.
            use_gui (bool): Whether to use a graphical interface.
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {client_id: (socket, address)}
        self.client_lock = threading.Lock()
        self.message_queue = []  # queue for messages
        self.queue_lock = threading.Lock()
        self.running = True  # added to control the server loop
        self.use_gui = use_gui

        if use_gui:
            self.root = tk.Tk()
            self.root.title("Message Server")
            self.root.geometry("600x400")
            self.font = font.Font(family="Arial", size=12)
            self.apply_theme() # Apply the theme here
            self.create_gui()
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # Handle window closing
        else:
            self.log_text = None

        self.start()

    def apply_theme(self):
        """Applies the black theme with custom colors."""
        self.root.config(bg="black")
        self.top_frame_bg = "gray15"
        self.middle_frame_bg = "gray15"
        self.label_fg = "lightgray"
        self.host_label_fg = "white"
        self.port_label_fg = "white"
        self.log_label_fg = "lightblue"
        self.error_fg = "red"  # Color for error messages
        self.connected_fg = "cyan"
        self.disconnected_fg = "yellow"
        self.received_fg = "magenta"
        self.sent_fg = "blue"
        self.started_fg = "green"
        self.stopped_fg = "red"
        self.warning_fg = "yellow"
        self.entry_bg = "gray25"
        self.entry_fg = "white"
        self.log_text_bg = "gray20"
        self.log_text_fg = "white"
        self.highlight_color = "springgreen" # Example highlight color

    def create_gui(self):
        """Creates the GUI elements for the server window."""
        self.top_frame = tk.Frame(self.root, bg=self.top_frame_bg)
        self.top_frame.pack(pady=10)

        self.host_label = tk.Label(self.top_frame, text="Host:", font=self.font, fg=self.host_label_fg, bg=self.top_frame_bg)
        self.host_label.grid(row=0, column=0, padx=5)
        self.host_entry = tk.Entry(self.top_frame, width=15, font=self.font,
                                   textvariable=tk.StringVar(value=self.host),
                                   bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.highlight_color)
        self.host_entry.grid(row=0, column=1, padx=5)
        self.host_entry.config(state=tk.DISABLED)  # Make Host entry disabled

        self.port_label = tk.Label(self.top_frame, text="Port:", font=self.font, fg=self.port_label_fg, bg=self.top_frame_bg)
        self.port_label.grid(row=0, column=2, padx=5)
        self.port_entry = tk.Entry(self.top_frame, width=10, font=self.font,
                                   textvariable=tk.StringVar(value=self.port),
                                   bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.highlight_color)
        self.port_entry.grid(row=0, column=3, padx=5)
        self.port_entry.config(state=tk.DISABLED)  # Make Port entry disabled

        self.middle_frame = tk.Frame(self.root, bg=self.middle_frame_bg)
        self.middle_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.log_label = tk.Label(self.middle_frame, text="Server Log:", font=self.font, fg=self.log_label_fg, bg=self.middle_frame_bg)
        self.log_label.pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(self.middle_frame, wrap=tk.WORD, height=10, font=self.font,
                                                   bg=self.log_text_bg, fg=self.log_text_fg, insertbackground=self.highlight_color)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    def start(self):
        """Starts the server to listen for client connections."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)  # Listen for up to 5 connections
            self.log(f"Server started on {self.host}:{self.port}", color=self.started_fg)
        except Exception as e:
            self.log(f"Error starting server: {e}", color=self.error_fg)
            return

        # Start a thread to handle incoming connections
        threading.Thread(target=self.accept_connections, daemon=True).start()
        threading.Thread(target=self.process_messages, daemon=True).start()  # start message processing thread

        if self.use_gui:
            self.root.mainloop()  # Start the Tkinter event loop
        else:
            while self.running:
                time.sleep(1)
            self.stop()

    def on_closing(self):
        """Handles the window closing event."""
        self.running = False
        self.stop() # Call stop to clean up sockets and threads
        if self.use_gui:
            self.root.destroy()

    def accept_connections(self):
        """Accepts incoming client connections and starts a new thread for each."""
        while self.running:  # use the running attribute
            try:
                client_socket, client_address = self.server_socket.accept()
                # Receive the initial ID message from the client
                client_id_data = client_socket.recv(1024).decode('utf-8')
                try:
                    client_id_json = json.loads(client_id_data)
                    if "id" in client_id_json:
                        client_id = client_id_json["id"]
                        with self.client_lock:
                            # check if client_id already exists
                            if client_id in self.clients:
                                self.log(f"Client ID {client_id} already exists.  Disconnecting new client.", color=self.warning_fg)
                                client_socket.send(json.dumps({"error": "ID already exists"}).encode('utf-8'))
                                client_socket.close()
                                continue
                            self.clients[client_id] = (client_socket, client_address)
                        self.log(f"Client {client_address} connected with ID: {client_id}", color=self.connected_fg)
                        client_socket.send(json.dumps({"status": "connected"}).encode('utf-8'))  # send connection status
                        # Start a thread to handle communication with this client
                        threading.Thread(target=self.handle_client, args=(client_id,), daemon=True).start()
                    else:
                        self.log(f"Client {client_address} did not send a valid ID. Disconnecting.", color=self.error_fg)
                        client_socket.send(json.dumps({"error": "Invalid ID format"}).encode('utf-8'))
                        client_socket.close()
                except json.JSONDecodeError:
                    self.log(f"Client {client_address} sent invalid JSON. Disconnecting.", color=self.error_fg)
                    client_socket.send(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                    client_socket.close()

            except socket.error:
                if self.running:  # check if server is running
                    self.log("Socket error while accepting connections.", color=self.error_fg)
                break  # Break the loop,

            except Exception as e:
                if self.running:
                    self.log(f"Error accepting connections: {e}", color=self.error_fg)
                break

    def handle_client(self, client_id):
        """
        Handles communication with a specific client.  Receives messages and puts them in queue.

        Args:
            client_id (str): The ID of the client to handle.
        """
        client_socket = self.clients[client_id][0]  # get socket
        while self.running:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break  # Client disconnected
                try:
                    message = json.loads(data)
                    if "target_id" in message and "text" in message:
                        # Add the message to the queue
                        with self.queue_lock:
                            self.message_queue.append(message)
                        self.log(f"Received message from {client_id} for {message['target_id']}: {message['text']}", color=self.received_fg)
                    else:
                        self.log(f"Client {client_id} sent invalid message format: {data}", color=self.error_fg)
                except json.JSONDecodeError:
                    self.log(f"Client {client_id} sent invalid JSON: {data}", color=self.error_fg)
            except socket.error:
                self.log(f"Socket error with client {client_id}", color=self.error_fg)
                break  # Client disconnected
            except Exception as e:
                self.log(f"Error handling client {client_id}: {e}", color=self.error_fg)
                break

        # Clean up when the client disconnects
        with self.client_lock:
            if client_id in self.clients:
                del self.clients[client_id]
        try:
            client_socket.close()
        except socket.error:
            pass  # ignore socket errors on close
        self.log(f"Client {client_id} disconnected.", color=self.disconnected_fg)

    def process_messages(self):
        """
        Processes messages from the queue and sends them to the appropriate clients.
        """
        while self.running:
            message = None # Initialize message here
            with self.queue_lock:
                if self.message_queue:
                    message = self.message_queue.pop(0)  # get first message
            if message:
                target_id = message["target_id"]
                with self.client_lock:
                    if target_id in self.clients:
                        target_socket = self.clients[target_id][0]
                        try:
                            target_socket.send(json.dumps(message).encode('utf-8'))
                            self.log(f"Sent message to {target_id}: {message['text']}", color=self.sent_fg)
                        except socket.error:
                            self.log(f"Error sending message to {target_id}.  Removing client.", color=self.error_fg)
                            with self.client_lock:
                                if target_id in self.clients:
                                    del self.clients[target_id]
                    else:
                        self.log(f"Client {target_id} not found.  Message dropped: {message['text']}", color=self.warning_fg)
            time.sleep(0.1)  # Don't consume CPU unnecessarily

    def stop(self):
        """Stops the server."""
        self.running = False  # set running to false
        self.log("Stopping server...", color=self.warning_fg)
        if self.server_socket:
            try:
                self.server_socket.close()
            except socket.error:
                pass # Ignore errors
        with self.client_lock:
            for client_id, (client_socket, _) in self.clients.items():
                try:
                    client_socket.close()
                except socket.error:
                    pass  # ignore errors
        self.log("Server stopped.", color=self.stopped_fg)

    def send_message(self, client_id, message):
        """Sends a message to a specific client. This is likely not needed.

        Args:
            client_id (str): The ID of the client to send the message to.
            message (str): The message to send.
        """
        with self.client_lock:
            if client_id in self.clients:
                client_socket = self.clients[client_id][0]
                try:
                    client_socket.send(message.encode('utf-8'))
                    return True  # Message sent successfully
                except socket.error:
                    self.log(f"Error sending message to client {client_id}", color=self.error_fg)
                    if client_id in self.clients:
                        del self.clients[client_id]  # Remove disconnected client
                    return False  # message failed to send
            else:
                self.log(f"Client {client_id} not found", color=self.warning_fg)
                return False  # Client not found

    def log(self, message, color=None):
        """
        Logs a message to the console or the GUI log with an optional color.

        Args:
            message (str): The message to log.
            color (str, optional): The foreground color for the GUI log. Defaults to None.
        """
        if self.use_gui and self.log_text:
            self.root.after(0, self._log_to_gui, message, color)  # Pass color to _log_to_gui
        else:
            if color:
                print(f"\033[91m{message}\033[0m" if color == "red" else message) # Basic console coloring
            else:
                print(message)

    def _log_to_gui(self, message, color=None):
        """Helper function to update the GUI log from the main thread with color."""
        self.log_text.config(state=tk.NORMAL)
        if color:
            self.log_text.tag_config(color, foreground=color)
            self.log_text.insert(tk.END, message + "\n", color)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Message Server.")
    parser.add_argument('--host', type=str, default='192.168.210.33', help='The host IP address to bind to.')
    parser.add_argument('--port', type=int, default=12345, help='The port number to listen on.')
    parser.add_argument('--no-gui', action='store_false', dest='use_gui',
                        help='Run the server without a graphical interface.')
    args = parser.parse_args()

    server = MessageServer(host=args.host, port=args.port, use_gui=args.use_gui)