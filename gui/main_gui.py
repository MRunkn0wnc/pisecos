import tkinter as tk
import sys
import os

# Add the core directory to the path
core_path = os.path.join(os.path.dirname(__file__), "..", "core")
sys.path.append(core_path)

from recon_engine import run_recon
from dashboard import Dashboard
from theme import *

root = tk.Tk()

root.title("PiSecOS Cyber Console")
root.geometry("1000x600")
root.configure(bg=BACKGROUND)

app = Dashboard(root,run_recon)
app.pack(fill="both",expand=True)

root.mainloop()
