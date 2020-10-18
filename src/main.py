import tkinter as tk
from pathlib import Path

import utils
from config import Config
from gui.analysis import Analysis
from gui.menu import Menu
from gui.styles import configure_styles

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Spotify Analyzer")
    root.iconbitmap(Path("resources") / "icon.ico")
    configure_styles(root)

    config = Config.load("config.toml")
    if config.enable_logs:
        utils.configure_logger("analyzer", "logs.txt")

    analysis = Analysis(root, config=config)
    analysis.gui.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    menu = Menu(root, on_load=analysis.on_load)
    root.config(menu=menu)

    root.mainloop()
