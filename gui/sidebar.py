import tkinter as tk
from theme import *

class Sidebar(tk.Frame):

    def __init__(self, parent):

        super().__init__(parent,bg=PANEL,width=200)

        title = tk.Label(
            self,
            text="PiSecOS",
            bg=PANEL,
            fg=PRIMARY,
            font=FONT_TITLE
        )
        title.pack(pady=20)

        self.add_button("Recon")
        self.add_button("Web Pentest")
        self.add_button("Network Scan")
        self.add_button("Reports")
        self.add_button("Settings")

    def add_button(self,text):

        btn = tk.Button(
            self,
            text=text,
            bg=BACKGROUND,
            fg=TEXT,
            activebackground=PRIMARY,
            relief="flat",
            font=FONT_MAIN
        )

        btn.pack(fill="x",pady=5,padx=10)
