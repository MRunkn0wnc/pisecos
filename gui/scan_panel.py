import tkinter as tk
from theme import *
import threading

class ScanPanel(tk.Frame):

    def __init__(self,parent,run_recon):

        super().__init__(parent,bg=BACKGROUND)

        self.run_recon = run_recon

        title = tk.Label(
            self,
            text="TARGET RECON",
            bg=BACKGROUND,
            fg=PRIMARY,
            font=FONT_TITLE
        )
        title.pack(pady=10)

        self.target = tk.Entry(
            self,
            bg="#000000",
            fg=ACCENT,
            insertbackground=ACCENT,
            font=FONT_MAIN
        )
        self.target.pack(pady=10)

        start = tk.Button(
            self,
            text="START SCAN",
            bg=PRIMARY,
            fg="black",
            font=FONT_MAIN,
            command=self.start_scan
        )
        start.pack(pady=10)

        self.output = tk.Text(
            self,
            bg="#000000",
            fg=CYAN,
            height=20,
            font=("Courier",10)
        )
        self.output.pack(fill="both",expand=True,padx=10,pady=10)

    def start_scan(self):

        target = self.target.get()

        if not target:
            return

        thread = threading.Thread(
            target=self.run_scan,
            args=(target,)
        )
        thread.start()

    def run_scan(self,target):

        self.output.insert("end",f"\n[+] Starting scan for {target}\n")

        self.run_recon(target)

        self.output.insert("end","\n[+] Scan completed\n")

