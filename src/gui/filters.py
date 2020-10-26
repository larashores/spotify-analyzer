import datetime
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any, List, Optional, Protocol, Set

import tzlocal
from backports import zoneinfo
from PIL import Image, ImageTk

import utils
from gui.calendarwidget import get_datetime
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
        self._clock_image = ImageTk.PhotoImage(Image.open("resources/clock.png").resize((13, 13)))

        start_label = ttk.Label(self, text="Start: ")
        self._start_var = tk.StringVar()
        self._start_entry = ttk.Entry(self, textvariable=self._start_var, justify=tk.CENTER)
        start_button = ttk.Button(self, image=self._clock_image, command=self._on_click_start)
        end_label = ttk.Label(self, text="End: ")
        self._end_var = tk.StringVar()
        self._end_entry = ttk.Entry(self, textvariable=self._end_var, justify=tk.CENTER)
        end_button = ttk.Button(self, image=self._clock_image, command=self._on_click_end)

        start_label.grid(row=0, column=0)
        self._start_entry.grid(row=0, column=1, sticky=tk.E + tk.W)
        start_button.grid(row=0, column=2)

        end_label.grid(row=1, column=0)
        self._end_entry.grid(row=1, column=1, sticky=tk.E + tk.W)
        end_button.grid(row=1, column=2)

        self.columnconfigure(1, weight=1)

    def _on_check(self) -> None:
        state = "!disabled" if self._title_var.get() else "disabled"
        self._start_entry.state([state])
        self._end_entry.state([state])

    def filter(self, tracks: List[Track]) -> List[Track]:
        if start := self._start_var.get():
            tracks = [track for track in tracks if datetime.datetime.fromisoformat(start) <= track.start]
        if end := self._end_var.get():
            tracks = [track for track in tracks if datetime.datetime.fromisoformat(end) >= track.end]
        return tracks

    def _on_click_start(self):
        start = get_datetime(self)
        if start is not None:
            self._start_var.set(start.date().isoformat())

    def _on_click_end(self):
        end = get_datetime(self)
        if end is not None:
            self._end_var.set(end.date().isoformat())


class Timezone(FilterWidget):
    def __init__(self, parent: Parent = None):
        super().__init__(parent)

        self._combo_var = tk.StringVar()
        label = ttk.Label(self, text="Timezone: ")
        combo = ttk.Combobox(self, values=sorted(zoneinfo.available_timezones()), textvariable=self._combo_var)

        label.pack(side=tk.LEFT)
        combo.pack(side=tk.LEFT, expand=True, fill=tk.X)

        combo.state(["readonly"])

        self._combo_var.set(tzlocal.get_localzone())

    def filter(self, tracks: List[Track]) -> List[Track]:
        if zone := self._combo_var.get():
            tracks = [track.to_timezone(zoneinfo.ZoneInfo(zone)) for track in tracks]

        return tracks
