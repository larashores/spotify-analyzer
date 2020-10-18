import abc
import tkinter as tk
from typing import List

from gui.components.component import Component
from track import Track
from type_hints import Parent


class TextComponent(Component):
    def __init__(self, parent: Parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._text = tk.Text(self, state="disabled")
        self._text.pack(expand=True, fill=tk.BOTH)

    def analyze(self, tracks: List[Track], *args) -> None:
        self._text.configure(state="normal")
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", self.text(tracks, *args))
        self._text.configure(state="disabled")

    @abc.abstractmethod
    def text(self, tracks: List[Track], *args) -> str:
        return NotImplemented
