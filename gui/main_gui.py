import tkinter as tk

from compact_dashboard import PiSecCompactUI
from theme import *

root = tk.Tk()

root.title("PiSecOS")
root.geometry("480x320")
root.configure(bg=BACKGROUND)

app = PiSecCompactUI(root)
app.pack(fill="both",expand=True)

root.mainloop()