# ui/panel.py
import tkinter as tk


class LogPanel:
    def __init__(self, parent_frame):
        self.frame = tk.LabelFrame(parent_frame, text=" Nhật Ký Hoạt Động ", font=("Segoe UI", 11, "bold"),
                                   bg="#ECF0F1", fg="#2C3E50", padx=10, pady=10)
        self.frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(self.frame, width=45, yscrollcommand=self.scrollbar.set, bg="#1E272E",
                                fg="#00D2D3", font=("Consolas", 11), relief=tk.FLAT, selectbackground="#485460")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.log_text.yview)

    def add_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def clear(self):
        self.log_text.delete('1.0', tk.END)