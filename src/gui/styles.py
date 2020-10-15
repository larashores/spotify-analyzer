import tkinter as tk
from tkinter import ttk

TITLE_FONT = ("tkdefaultfont", 16, "bold")
SUBTITLE_FONT = ("tkdefaultfont", 11, "bold")


def configure_styles(parent: tk.Widget):
    style = ttk.Style(parent)
    style.configure("Title.TLabel", font=TITLE_FONT)
    style.configure("Subtitle.TLabel", font=SUBTITLE_FONT)
    style.configure("Action.TButton", width=8)
    style.configure("TCombobox", width=5)
