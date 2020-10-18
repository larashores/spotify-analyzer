import abc
import tkinter as tk
from typing import Iterable, List

import matplotobjlib as plot

from gui.components.component import Component
from track import Track
from type_hints import Parent


class PlotComponent(Component):
    def __init__(self, parent: Parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._figure = None

    def analyze(self, tracks: List[Track], *args) -> None:
        if self._figure:
            self._figure.destroy()
        self._figure = plot.TkFigure(
            self,
            [[plot.SubPlot(*self.graphs(tracks, *args))]],
            adjust=plot.SubplotsAdjust(left=0.05, right=0.975, top=0.975, bottom=0.08),
        )
        self._figure.pack(expand=True, fill=tk.BOTH)  # type: ignore

    @abc.abstractmethod
    def graphs(self, tracks: List[Track]) -> Iterable[plot.Graph]:
        return NotImplemented
