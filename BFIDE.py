import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk, scrolledtext
# import threading # Removed threading import

BF_COMMANDS = "><+-.,[]"

class BrainfuckInterpreter:
    def __init__(self, code, input_data=''):
        self.code = [c for c in code if c in BF_COMMANDS]
        self.input_data = list(input_data)
        self.input_data.reverse()
        self.output = ''
        self.cells = [0] * 30000
        self.ptr = 0
        self.pc = 0
        self.bracket_map = self.build_bracket_map()
        self.running = True

    def build_bracket_map(self):
        stack = []
        map = {}
        for pos, cmd in enumerate(self.code):
            if cmd == '[':
                stack.append(pos)
            elif cmd == ']':
                if not stack:
                    raise SyntaxError("Unmatched ']' at position {}".format(pos))
                start = stack.pop()
                map[start] = pos
                map[pos] = start
        if stack:
            raise SyntaxError("Unmatched '[' at position {}".format(stack.pop()))
        return map

    def step(self):
        if not self.running or self.pc >= len(self.code):
            self.running = False
            return None

        cmd = self.code[self.pc]
        if cmd == '>':
            self.ptr += 1
        elif cmd == '<':
            self.ptr -= 1
        elif cmd == '+':
            self.cells[self.ptr] = (self.cells[self.ptr] + 1) % 256
        elif cmd == '-':
            self.cells[self.ptr] = (self.cells[self.ptr] - 1) % 256
        elif cmd == '.':
            self.output += chr(self.cells[self.ptr])
        elif cmd == ',':
            self.cells[self.ptr] = ord(self.input_data.pop()) if self.input_data else 0
        elif cmd == '[':
            if self.cells[self.ptr] == 0:
                self.pc = self.bracket_map[self.pc]
        elif cmd == ']':
            if self.cells[self.ptr] != 0:
                self.pc = self.bracket_map[self.pc]

        self.pc += 1
        return self.cells, self.ptr, self.output

    def run_all(self):
        """Runs the Brainfuck code to completion (synchronously)."""
        while self.running and self.pc < len(self.code):
            self.step()
        return self.output


class BrainfuckIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Brainfuck IDE - Dark Mode")
        self.geometry("900x600")
        self.configure(bg="#1e1e1e")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background="#1e1e1e", foreground="white", fieldbackground="#2d2d2d")

        # --- Code Editor Section (Fixed Layout) ---
        # Create a frame to hold both the line numbers and the editor
        editor_frame_container = tk.Frame(self, bg="#1e1e1e")
        editor_frame_container.pack(fill="both", expand=True, pady=5) # Pack this container

        # Line number display - now parented to editor_frame_container
        self.line_number_canvas = tk.Canvas(editor_frame_container, width=40, bg="#2d2d2d", bd=0, highlightthickness=0)
        self.line_number_canvas.pack(side="left", fill="y", padx=(5,0)) # Pack to the left within the container

        # Editor scrolledtext - now parented to editor_frame_container
        self.editor = scrolledtext.ScrolledText(editor_frame_container, height=10, font=("Courier", 12), undo=True,
                                                 bg="#1e1e1e", fg="white", insertbackground="white",
                                                 wrap=tk.NONE) # Added wrap=tk.NONE for better code display
        self.editor.pack(side="left", fill="both", expand=True) # Pack to the left, expanding
        self.editor.bind("<KeyRelease>", self.highlight_syntax)
        
        # Bind scrolling to update line numbers
        self.editor.bind("<MouseWheel>", self.update_line_numbers_scroll)
        self.editor.bind("<Button-4>", self.update_line_numbers_scroll) # Linux scroll up
        self.editor.bind("<Button-5>", self.update_line_numbers_scroll) # Linux scroll down
        self.editor.vbar.config(command=self.editor.yview) # Ensure editor's scrollbar updates line numbers
        self.editor.config(yscrollcommand=self.on_editor_scroll)


        # --- Controls Frame ---
        control_frame = tk.Frame(self, bg="#1e1e1e")
        control_frame.pack(fill="x", pady=5)

        tk.Label(control_frame, text="Input:", bg="#1e1e1e", fg="white").pack(side="left", padx=(10, 0))
        self.input_entry = tk.Entry(control_frame, width=20, bg="#2d2d2d", fg="white", insertbackground="white")
        self.input_entry.pack(side="left", padx=5)

        # Reverted Run button command to synchronous run_code
        self.run_button = tk.Button(control_frame, text="Run", command=self.run_code, bg="#2d2d2d", fg="white")
        self.run_button.pack(side="left", padx=5)
        
        self.step_button = tk.Button(control_frame, text="Step", command=self.step_code, bg="#2d2d2d", fg="white")
        self.step_button.pack(side="left", padx=5)
        
        self.reset_button = tk.Button(control_frame, text="Reset", command=self.reset_code, bg="#2d2d2d", fg="white")
        self.reset_button.pack(side="left", padx=5)
        
        self.save_button = tk.Button(control_frame, text="Save", command=self.save_code, bg="#2d2d2d", fg="white")
        self.save_button.pack(side="left", padx=5)
        
        self.load_button = tk.Button(control_frame, text="Load", command=self.load_code, bg="#2d2d2d", fg="white")
        self.load_button.pack(side="left", padx=5)
        
        self.export_button = tk.Button(control_frame, text="Export Optimized", command=self.export_optimized_code, bg="#2d2d2d", fg="white")
        self.export_button.pack(side="left", padx=5)

        # --- Output ---
        tk.Label(self, text="Output:", bg="#1e1e1e", fg="white").pack(anchor="w", padx=10, pady=(5,0))
        self.output_box = scrolledtext.ScrolledText(self, height=6, font=("Courier", 12), state="disabled",
                                                     bg="#1e1e1e", fg="white", insertbackground="white")
        self.output_box.pack(fill="x", padx=10, pady=(0,5))

        # --- Memory Tape ---
        tk.Label(self, text="Memory Tape:", bg="#1e1e1e", fg="white").pack(anchor="w", padx=10, pady=(5,0))
        self.tape_frame = tk.Frame(self, bg="#1e1e1e")
        self.tape_frame.pack(fill="x", padx=10, pady=(0,5))
        self.tape_cells = []

        for i in range(20):  # Display first 20 cells
            cell = tk.Label(self.tape_frame, text="0", width=4, borderwidth=2, relief="groove",
                            bg="#2d2d2d", fg="white")
            cell.pack(side="left", padx=1, pady=2)
            self.tape_cells.append(cell)

        self.interpreter = None

        # Initial update for line numbers
        self.update_line_numbers()
        
    def highlight_syntax(self, event=None):
        # Remove existing tags
        for tag in ["gtlt", "plusminus", "brackets", "dot", "comma"]:
            self.editor.tag_remove(tag, "1.0", tk.END)

        tags = {
            '>': ("gtlt", "blue"),
            '<': ("gtlt", "blue"),
            '+': ("plusminus", "lime green"),
            '-': ("plusminus", "lime green"),
            '[': ("brackets", "orange"),
            ']': ("brackets", "orange"),
            '.': ("dot", "cyan"),
            ',': ("comma", "magenta") 
        }

        for cmd, (tag, color) in tags.items():
            self.editor.tag_config(tag, foreground=color)
            start = "1.0"
            while True:
                pos = self.editor.search(cmd, start, stopindex=tk.END, regexp=False) # Use regexp=False for literal search
                if not pos:
                    break
                end = f"{pos}+1c"
                self.editor.tag_add(tag, pos, end)
                start = end

        self.update_line_numbers()

    def update_line_numbers(self):
        # Calculate how many lines are currently in the Text widget
        total_lines = int(self.editor.index('end-1c').split('.')[0])
        
        # Get the visible range of lines in the editor
        first_visible_line = int(self.editor.index("@0,0").split('.')[0])
        last_visible_line = int(self.editor.index(f"@0,{self.editor.winfo_height()}").split('.')[0]) + 1
        
        self.line_number_canvas.delete("all")
        
        # Iterate through visible lines and draw their numbers
        for i in range(first_visible_line, max(total_lines + 1, last_visible_line)):
            # Get the y-coordinate of the current line's text
            dline_info = self.editor.dlineinfo(f"{i}.0")
            if dline_info:
                y_pos = dline_info[1]
                self.line_number_canvas.create_text(
                    2, y_pos, 
                    anchor="nw", 
                    text=str(i), 
                    fill="white",
                    font=("Courier", 12) # Match editor font size
                )

    def on_editor_scroll(self, *args):
        # Sync the vertical scrollbar of the editor with the line numbers
        self.line_number_canvas.yview_moveto(args[0])
        self.update_line_numbers() # Recalculate and redraw line numbers based on new scroll position

    def update_line_numbers_scroll(self, event):
        # Propagate scroll events from the canvas to the editor
        self.editor.yview_scroll(-1 * (event.delta // 120), "units")
        self.update_line_numbers()

    def run_code(self):
        """
        Executes the Brainfuck code synchronously (on the main thread).
        May cause UI freeze for very long-running programs.
        """
        code = self.editor.get("1.0", "end-1c")
        input_data = self.input_entry.get()
        
        # Disable buttons during execution (will re-enable at end)
        self.run_button.config(state=tk.DISABLED)
        self.step_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED) 
        self.save_button.config(state=tk.DISABLED)
        self.load_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)

        try:
            self.interpreter = BrainfuckInterpreter(code, input_data)
            self.display_output("Running Brainfuck code...") # Initial message
            self.update_memory()

            output = self.interpreter.run_all() # This is the synchronous call
            
            self.display_output(output) # Display final output
            self.update_memory() # Update memory one last time
            messagebox.showinfo("Execution Finished", "Brainfuck program execution completed.")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            # Always re-enable buttons
            self.run_button.config(state=tk.NORMAL)
            self.step_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            self.load_button.config(state=tk.NORMAL)
            self.export_button.config(state=tk.NORMAL)


    def step_code(self):
        if not self.interpreter:
            code = self.editor.get("1.0", "end-1c")
            input_data = self.input_entry.get()
            try:
                self.interpreter = BrainfuckInterpreter(code, input_data)
                self.display_output("Stepping through code...")
                self.update_memory()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                return
        
        result = self.interpreter.step()
        if result:
            _, ptr, output = result
            self.display_output(output)
            self.update_memory()
            # Check if execution finished after this step
            if not self.interpreter.running or self.interpreter.pc >= len(self.interpreter.code):
                messagebox.showinfo("Execution Finished", "Program execution completed.")
        else:
            messagebox.showinfo("Execution Finished", "Program execution completed (no more steps).")


    def reset_code(self):
        self.interpreter = None
        self.display_output("")
        self.update_memory([0] * 20)
        # Ensure buttons are enabled after reset, as no _execution_finished() is called automatically
        self.run_button.config(state=tk.NORMAL)
        self.step_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        self.load_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)


    def display_output(self, text):
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)
        self.output_box.config(state='disabled')

    def update_memory(self, cells=None):
        if not self.interpreter:
            for label in self.tape_cells:
                label.config(text="0", bg="#2d2d2d") # Reverted to dark mode default
            return

        tape = self.interpreter.cells
        ptr = self.interpreter.ptr
        for i in range(20):
            val = tape[i]
            bg = "#8a7500" if i == ptr else "#2d2d2d"
            self.tape_cells[i].config(text=str(val), bg=bg)

    def save_code(self):
        code = self.editor.get("1.0", "end-1c")
        file_path = filedialog.asksaveasfilename(defaultextension=".b", filetypes=[("Brainfuck files", "*.b")])
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(code)
                messagebox.showinfo("Save Complete", "Code saved successfully!")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file: {e}")


    def load_code(self):
        file_path = filedialog.askopenfilename(filetypes=[("Brainfuck files", "*.b"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.editor.delete("1.0", tk.END)
                    self.editor.insert(tk.END, f.read())
                self.highlight_syntax()
                self.reset_code() # Reset interpreter state after loading new code
                messagebox.showinfo("Load Complete", "Code loaded successfully!")
            except Exception as e:
                messagebox.showerror("Load Error", f"Could not load file: {e}")


    def export_optimized_code(self):
        code = self.editor.get("1.0", "end-1c")
        optimized_code = self.optimize_brainfuck(code)
        file_path = filedialog.asksaveasfilename(defaultextension=".b", filetypes=[("Brainfuck files", "*.b")])
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(optimized_code)
                messagebox.showinfo("Export Complete", "Optimized code exported successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export file: {e}")


    def optimize_brainfuck(self, code):
        """
        Removes non-Brainfuck characters from the code.
        Note: For actual Brainfuck optimization (e.g., combining `+++` or detecting `[-]`),
        a more advanced parsing and optimization algorithm would be needed.
        """
        clean_code = [c for c in code if c in BF_COMMANDS]
        return ''.join(clean_code)


if __name__ == "__main__":
    app = BrainfuckIDE()
    app.mainloop()