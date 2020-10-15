import abc
from tkinter import ttk
from typing import Any, List, Sequence

from gui.options import Option
from track import Track


class Component(ttk.Frame, metaclass=abc.ABCMeta):
    name: str
    dim = (600, 400)
    options: Sequence[Option] = tuple()

    @abc.abstractmethod
    def analyze(self, tracks: List[Track], *args: Any) -> None:
        return
