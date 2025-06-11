import http.server
import socketserver
import threading
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class SimpleWebServer:
    def __init__(self, master):
        self.master = master
        master.title("Simple Multi-Directory Web Server")

        self.servers = {}
        self.server_threads = {}

        self.style = ttk.Style(master)
        self.style.theme_use('clam')

        self.create_widgets()

    def create_widgets(self):
        self.add_server_frame = ttk.LabelFrame(self.master, text="Add New Server")
        self.add_server_frame.pack(padx=10, pady=10, fill=tk.X)

        ttk.Label(self.add_server_frame, text="IP Address:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ip_entry = ttk.Entry(self.add_server_frame)
        self.ip_entry.insert(0, "0.0.0.0")  # Default to listen on all interfaces
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(self.add_server_frame, text="Port:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_entry = ttk.Entry(self.add_server_frame)
        self.port_entry.insert(0, "8000")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(self.add_server_frame, text="Folder:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.folder_entry = ttk.Entry(self.add_server_frame)
        self.folder_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        self.browse_button = ttk.Button(self.add_server_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=2, column=2, padx=5, pady=5, sticky=tk.E)

        self.start_button = ttk.Button(self.add_server_frame, text="Start Server", command=self.start_new_server)
        self.start_button.grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky=tk.EW)

        self.running_servers_frame = ttk.LabelFrame(self.master, text="Running Servers")
        self.running_servers_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.server_list = tk.Listbox(self.running_servers_frame)
        self.server_list.pack(fill=tk.BOTH, expand=True)

        self.stop_button = ttk.Button(self.running_servers_frame, text="Stop Selected Server", command=self.stop_selected_server, state=tk.DISABLED)
        self.stop_button.pack(pady=5, fill=tk.X)
        self.server_list.bind('<<ListboxSelect>>', self.enable_stop_button)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def start_new_server(self):
        ip_address = self.ip_entry.get()
        try:
            port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number.")
            return
        folder = self.folder_entry.get()

        if not os.path.isdir(folder):
            messagebox.showerror("Error", f"Folder '{folder}' does not exist.")
            return

        server_address = (ip_address, port)

        try:
            handler = self.create_handler(folder)
            httpd = socketserver.TCPServer(server_address, handler)
            thread = threading.Thread(target=httpd.serve_forever)
            thread.daemon = True
            thread.start()

            server_key = f"{ip_address}:{port}"
            self.servers[server_key] = httpd
            self.server_threads[server_key] = thread
            self.server_list.insert(tk.END, server_key + f" serving '{folder}'")
            self.clear_input_fields()
            messagebox.showinfo("Info", f"Server started on http://{ip_address}:{port} serving '{folder}'.")

        except Exception as e:
            messagebox.showerror("Error", f"Could not start server: {e}")

    def create_handler(self, directory):
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=directory, **kwargs)
        return Handler

    def stop_selected_server(self):
        selected_index = self.server_list.curselection()
        if selected_index:
            server_key = self.server_list.get(selected_index[0]).split(" ")[0]
            if server_key in self.servers:
                server = self.servers[server_key]
                server.shutdown()
                del self.servers[server_key]
                del self.server_threads[server_key]
                self.server_list.delete(selected_index[0])
                self.stop_button.config(state=tk.DISABLED)
                messagebox.showinfo("Info", f"Server '{server_key}' stopped.")
        else:
            messagebox.showinfo("Info", "No server selected to stop.")

    def enable_stop_button(self, event):
        if self.server_list.curselection():
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.stop_button.config(state=tk.DISABLED)

    def clear_input_fields(self):
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, "0.0.0.0")
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, "8000")
        self.folder_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleWebServer(root)
    root.mainloop()