import abc
import tkinter as tk
from typing import Iterable, List

import matplotobjlib as plot

from gui.components.component import Component
from track import Track
from type_hints import Parent


class PlotComponent(Component):
    adjust = plot.SubplotsAdjust(left=0.07, right=0.975, top=0.975, bottom=0.08)

    def __init__(self, parent: Parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._figure = None

    def analyze(self, tracks: List[Track], *args) -> None:
        if self._figure:
            self._figure.destroy()
        self._figure = plot.TkFigure(self, plot.FigureOptions([[self.subplot(tracks, *args)]], adjust=self.adjust))
        self._figure.pack(expand=True, fill=tk.BOTH)  # type: ignore

    @abc.abstractmethod
    def subplot(self, tracks: List[Track]) -> plot.SubPlot:
        return NotImplemented
