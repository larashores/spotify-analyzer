import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional, Protocol, Set

import utils
from gui.searchablecombobox import SearchableComboBox
from track import Track
from type_hints import Parent


class FilterWidget(ttk.Frame):
    def filter(self, tracks: List[Track]) -> List[Track]:
        return tracks


class Filter(Protocol):
    def __call__(self, parent: Parent = None) -> FilterWidget:
        ...


class DateRangeFilter(FilterWidget):
    def __init__(self, parent: Parent = None):
        super().__init__(parent)
        label = ttk.Label(self, text="Date Range")
        label.pack()
