import tkinter as tk
from tkinter.filedialog import askdirectory
from typing import Callable, Optional

from type_hints import Parent


class Menu(tk.Menu):
    def __init__(self, parent: Parent, *, on_load: Optional[Callable[[str], None]] = None):
        tk.Menu.__init__(self, parent)
        if parent:
            self._top_level = parent.winfo_toplevel()
            self._base_title = self._top_level.wm_title()
        else:
            self._top_level = None
            self._base_title = ""

        self._file_menu = tk.Menu(self, tearoff=False)
        self._file_menu.add_command(label="Load", command=self._on_load)
        self.add_cascade(label="File", menu=self._file_menu)

        self.bind_all("<Control-o>", lambda event: self._on_load())
        self.bind_all("<Control-O>", lambda event: self._on_load())

        self._on_load_callback = on_load

    def _on_load(self) -> None:
        path = askdirectory(
            title="Select folder containing Spotify data",
        )
        if path and self._on_load_callback:
            if self._top_level:
                self._top_level.wm_title("{} - {}".format(path, self._base_title))
            self._on_load_callback(path)
