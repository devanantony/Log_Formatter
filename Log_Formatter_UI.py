import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ModernLogCleaner:
    """
    Removes UART binary/noise from text logs while preserving normal ASCII
    log messages, timestamps, tabs, and line endings.
    """

    TIMESTAMP_RE = re.compile(rb"^(\[[^\]\r\n]+\]\s*)")

    def __init__(self, root):
        self.root = root
        self.root.title("UART Log Cleaner")
        self.root.geometry("650x390")
        self.root.configure(bg="#1e1e2e")

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TLabel",
            background="#1e1e2e",
            foreground="#ffffff",
            font=("Segoe UI", 11),
        )
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", padding=5)

        self.file_path = tk.StringVar()
        self.overwrite = tk.BooleanVar(value=False)
        self.remove_binary_lines = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root, bg="#1e1e2e")
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        title = tk.Label(
            frame,
            text="UART Log Cleaner",
            bg="#1e1e2e",
            fg="#89b4fa",
            font=("Segoe UI", 18, "bold"),
        )
        title.pack(pady=(0, 18))

        entry = ttk.Entry(frame, textvariable=self.file_path, width=65)
        entry.pack(pady=8)

        ttk.Button(
            frame, text="Browse Log File", command=self.browse_file
        ).pack(pady=5)

        ttk.Checkbutton(
            frame,
            text="Overwrite original file",
            variable=self.overwrite,
        ).pack(pady=5)

        ttk.Checkbutton(
            frame,
            text="Remove lines containing raw binary UART data",
            variable=self.remove_binary_lines,
        ).pack(pady=5)

        ttk.Button(
            frame, text="Clean File", command=self.clean_file
        ).pack(pady=18)

        self.status = tk.Label(
            frame,
            text="",
            bg="#1e1e2e",
            fg="#a6e3a1",
            font=("Segoe UI", 10),
            wraplength=590,
            justify="center",
        )
        self.status.pack(pady=5)

    def browse_file(self):
        selected = filedialog.askopenfilename(
            filetypes=[
                ("Log/Text files", "*.log *.txt"),
                ("All files", "*.*"),
            ]
        )
        if selected:
            self.file_path.set(selected)

    @staticmethod
    def is_printable_ascii(byte):
        # Keep normal printable ASCII and horizontal tab.
        return byte == 0x09 or 0x20 <= byte <= 0x7E

    def clean_content(self, content):
        cleaned_lines = []
        removed_binary_lines = 0
        removed_bytes = 0

        for line in content.splitlines(keepends=True):
            # Preserve CR/LF exactly as line terminators.
            if line.endswith(b"\r\n"):
                body, ending = line[:-2], b"\r\n"
            elif line.endswith(b"\n") or line.endswith(b"\r"):
                body, ending = line[:-1], line[-1:]
            else:
                body, ending = line, b""

            # Keep the timestamp prefix if a line is mostly binary.
            match = self.TIMESTAMP_RE.match(body)
            prefix = match.group(1) if match else b""
            payload = body[len(prefix):]

            non_printable = sum(
                1 for b in payload if not self.is_printable_ascii(b)
            )
            payload_length = len(payload)

            # The UART log contains raw diagnostic frames printed as text.
            # If a line has a substantial amount of binary data, discard its
            # payload rather than leaving fragments such as "~@" or "XV/SD".
            binary_ratio = (
                non_printable / payload_length if payload_length else 0
            )

            if (
                self.remove_binary_lines.get()
                and payload_length >= 4
                and binary_ratio >= 0.20
            ):
                cleaned_lines.append(prefix + ending)
                removed_binary_lines += 1
                removed_bytes += len(payload)
                continue

            # Remove all control bytes and non-ASCII bytes, but retain TAB.
            filtered = bytes(
                b for b in body if self.is_printable_ascii(b)
            )
            removed_bytes += len(body) - len(filtered)
            cleaned_lines.append(filtered + ending)

        return b"".join(cleaned_lines), removed_binary_lines, removed_bytes

    def clean_file(self):
        path = self.file_path.get().strip()

        if not path:
            messagebox.showerror("Error", "Please select a file first.")
            return

        extension = os.path.splitext(path)[1].lower()
        if extension not in (".log", ".txt"):
            messagebox.showerror(
                "Error", "Only .log and .txt files are supported."
            )
            return

        try:
            with open(path, "rb") as file:
                original = file.read()

            cleaned, binary_lines, removed_bytes = self.clean_content(original)

            if self.overwrite.get():
                output_path = path
            else:
                base, extension = os.path.splitext(path)
                output_path = f"{base}_cleaned{extension}"

            with open(output_path, "wb") as file:
                file.write(cleaned)

            self.status.config(
                text=(
                    f"Cleaned successfully. Removed {removed_bytes} "
                    f"unwanted bytes and {binary_lines} binary-data lines.\n"
                    f"Output: {output_path}"
                )
            )
            messagebox.showinfo(
                "Cleaning complete",
                f"Removed {removed_bytes} unwanted bytes.\n"
                f"Removed {binary_lines} binary-data lines.\n\n"
                f"Saved to:\n{output_path}",
            )

        except Exception as error:
            messagebox.showerror("Error", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernLogCleaner(root)
    root.mainloop()
