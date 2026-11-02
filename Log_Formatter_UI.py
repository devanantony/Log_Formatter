import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os

class ModernLogCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Cleaner - NUL & ESC Remover")
        self.root.geometry("600x350")
        self.root.configure(bg="#1e1e2e")

        style = ttk.Style()
        style.theme_use("default")

        style.configure("TLabel", background="#1e1e2e", foreground="#ffffff", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", padding=5)

        self.file_path = tk.StringVar()
        self.overwrite = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root, bg="#1e1e2e")
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        title = tk.Label(frame, text="Log Cleaner Tool", bg="#1e1e2e",
                            fg="#89b4fa", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(0, 20))

        entry = ttk.Entry(frame, textvariable=self.file_path, width=50)
        entry.pack(pady=10)

        browse_btn = ttk.Button(frame, text="Browse Log File", command=self.browse_file)
        browse_btn.pack(pady=5)

        overwrite_check = ttk.Checkbutton(frame, text="Overwrite original file",
                                            variable=self.overwrite)
        overwrite_check.pack(pady=5)

        clean_btn = ttk.Button(frame, text="Clean File", command=self.clean_file)
        clean_btn.pack(pady=20)

        self.status = tk.Label(frame, text="", bg="#1e1e2e",
                                fg="#a6e3a1", font=("Segoe UI", 10))
        self.status.pack()

    def browse_file(self):
        file = filedialog.askopenfilename(
            filetypes=[("Log/Text files", "*.log *.txt"), ("All files", "*.*")]
        )
        if file:
            self.file_path.set(file)

    def clean_file(self):
        path = self.file_path.get()

        if not path:
            messagebox.showerror("Error", "Please select a file first.")
            return

        # Validate extension
        ext = os.path.splitext(path)[1].lower()
        if ext not in [".log", ".txt"]:
            messagebox.showerror("Error", "Only .log and .txt files are supported.")
            return

        try:
            with open(path, "rb") as f:
                content = f.read()

            # Remove NUL (0x00) and ESC (0x1B)
            cleaned = content.replace(b"\x00", b"").replace(b"\x1B", b"")

            if self.overwrite.get():
                with open(path, "wb") as f:
                    f.write(cleaned)
                self.status.config(text="Original file overwritten successfully")
            else:
                base, ext = os.path.splitext(path)
                output_path = f"{base}_cleaned{ext}"

                with open(output_path, "wb") as f:
                    f.write(cleaned)

                self.status.config(text=f"Cleaned file saved: {output_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernLogCleaner(root)
    root.mainloop()