import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from type_hints import Parent


class OptionWidget(ttk.Frame):
    def get_value(self) -> Any:
        pass


Option = Callable[[tk.Widget], OptionWidget]


class _CheckButton(OptionWidget):
    def __init__(self, parent: Parent, *, text: str):
        super().__init__(parent)
        self._var = tk.IntVar(self)
        check = ttk.Checkbutton(self, text=text, variable=self._var)
        check.pack()
        self._var.set(0)

    def get_value(self) -> bool:
        return bool(self._var.get())


class CheckButton:
    def __init__(self, text: str):
        self._text = text

    def __call__(self, parent: Parent) -> OptionWidget:
        return _CheckButton(parent, text=self._text)
