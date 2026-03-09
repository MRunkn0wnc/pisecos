#!/usr/bin/env python3

import tkinter as tk
import threading

from theme import *
from recon_engine import run_recon


class PiSecCompactUI(tk.Frame):

    def __init__(self,parent):

        super().__init__(parent,bg=BACKGROUND)

        self.init_ui()


    def init_ui(self):

        # Title
        title = tk.Label(
            self,
            text="PiSecOS",
            bg=BACKGROUND,
            fg=PRIMARY,
            font=FONT_TITLE
        )
        title.pack(pady=5)


        # Target entry
        self.target = tk.Entry(
            self,
            bg="#000000",
            fg=ACCENT,
            insertbackground=ACCENT,
            font=FONT_MAIN
        )

        self.target.pack(fill="x",padx=10,pady=5)


        # Button grid
        button_frame = tk.Frame(self,bg=BACKGROUND)
        button_frame.pack(pady=5)


        self.make_button(button_frame,"RECON",self.recon).grid(row=0,column=0,padx=5,pady=5)
        self.make_button(button_frame,"ATTACK",self.attack).grid(row=0,column=1,padx=5,pady=5)

        self.make_button(button_frame,"TOOLS",self.tools).grid(row=1,column=0,padx=5,pady=5)
        self.make_button(button_frame,"REPORT",self.report).grid(row=1,column=1,padx=5,pady=5)


        # Terminal output
        self.output = tk.Text(
            self,
            bg="#000000",
            fg=CYAN,
            height=10,
            font=("Courier",8)
        )

        self.output.pack(fill="both",expand=True,padx=10,pady=5)


    def make_button(self,parent,text,cmd):

        return tk.Button(
            parent,
            text=text,
            width=12,
            bg=PRIMARY,
            fg="black",
            font=FONT_MAIN,
            command=cmd
        )


    def log(self,msg):

        self.output.insert("end",msg+"\n")
        self.output.see("end")


    def recon(self):

        target = self.target.get()

        if not target:
            self.log("[!] No target")
            return

        self.log(f"[+] Recon started: {target}")

        threading.Thread(
            target=self.run_recon,
            args=(target,)
        ).start()


    def run_recon(self,target):

        run_recon(target)

        self.log("[+] Recon completed")


    def attack(self):

        self.log("[+] Attack module coming soon")


    def tools(self):

        self.log("[+] Tool browser coming soon")


    def report(self):

        self.log("[+] Report generator coming soon")