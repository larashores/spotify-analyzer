import logging
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning
from typing import List, Optional

from config import Config
from gui import utils
from gui.components.artistsplot import ArtistsPlot
from gui.components.component import Component
from gui.components.monthlylistens import MonthlyListens
from gui.components.topartists import TopArtistsByDuration, TopArtistsByListens
from gui.components.totaltracks import TotalTracks
from gui.options import OptionWidget
from track import Track

logger = logging.getLogger(f"analysis.{__name__}")

COMPONENTS = (ArtistsPlot, MonthlyListens, TopArtistsByDuration, TopArtistsByListens, TotalTracks)


class AnalysisWidgets(ttk.Frame):
    def __init__(self, parent: tk.Widget):
        super().__init__(parent)

        sidebar_frame = ttk.Frame(self)
        sidebar_label = ttk.Label(sidebar_frame, text="Options", style="Subtitle.TLabel")
        self.options_frame = ttk.Frame(sidebar_frame)
        sidebar_button_seperator = ttk.Separator(sidebar_frame)
        self.sidebar_button = ttk.Button(sidebar_frame, text="Analyze")
        sidebar_seperator = ttk.Separator(self, orient=tk.VERTICAL)

        choice_frame = ttk.Frame(self)
        self.choice_var = tk.StringVar(choice_frame)
        choice_label = ttk.Label(choice_frame, text="Analyzer: ")
        self.choice_combo = ttk.Combobox(choice_frame, justify=tk.CENTER, textvariable=self.choice_var)

        self.analysis_frame = ttk.Frame(self)

        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_label.pack()
        self.options_frame.pack()
        sidebar_button_seperator.pack(fill=tk.X, padx=5, pady=5)
        self.sidebar_button.pack(padx=30, pady=(0, 30), anchor=tk.N)

        sidebar_seperator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        choice_frame.pack(side=tk.TOP, fill=tk.BOTH)
        choice_label.pack(side=tk.LEFT)
        self.choice_combo.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.analysis_frame.pack(expand=True, fill=tk.BOTH)


class Analysis:
    def __init__(self, parent: tk.Widget, *, config: Config):
        self.gui = AnalysisWidgets(parent)

        self._tracks: Optional[List[Track]] = None
        self._current_choice: Optional[str] = None
        self._current_component: Optional[Component] = None
        self._options: List[OptionWidget] = []
        self._component_map = {component.name: component for component in COMPONENTS}  # pylint: disable=no-member
        if config.component_directory is not None:
            for component in utils.load_components(config.component_directory):
                self._component_map[component.name] = component
        names = sorted(self._component_map.keys())

        self.gui.sidebar_button.config(command=self._on_analyze)
        self.gui.choice_combo.config(values=names)
        self.gui.choice_combo.state(["readonly"])
        self.gui.choice_combo.bind("<<ComboboxSelected>>", self._on_select)

        if self._component_map:
            self.gui.choice_var.set(names[0])
            self._on_select()

    def _on_select(self, _event: Optional[tk.Event] = None) -> None:
        choice = self.gui.choice_var.get()
        if choice != self._current_choice:
            component_type = self._component_map[choice]
            try:
                width, height = component_type.dim
                component = component_type(self.gui.analysis_frame, width=width, height=height)  # type: ignore
            except Exception as err:  # pylint: disable=broad-except
                logger.exception("Error creating analyzer of type %r", choice)
                showerror("Error", message=f"Error creating analyzer of type {choice!r}: {err}")
                self.gui.choice_var.set(self._current_choice)  # type: ignore
            else:
                if self._current_component:
                    self._current_component.destroy()

                for widget in self._options:
                    widget.destroy()
                self._options.clear()

                for option in component_type.options:
                    widget = option(self.gui.options_frame)
                    widget.pack(fill=tk.BOTH, anchor=tk.CENTER)
                    self._options.append(widget)

                component.pack(expand=True, fill=tk.BOTH)
                self._last_choice = choice
                self._current_component = component
                self._on_analyze()
                self._current_choice = choice
                self._current_component = component

                self.gui.update()

    def _on_analyze(self) -> None:
        if self._tracks is not None:
            try:
                self._current_component.analyze(self._tracks, *(widget.get_value() for widget in self._options))  # type: ignore
            except Exception as err:  # pylint: disable=broad-except
                logger.exception("Error analyzing data")
                showerror(title="Error", message=f"Error analyzing data: {err}")

    def on_load(self, path: str) -> None:
        result = utils.load_tracks(path)
        if result.errors:
            showwarning(title="Warning", message=f"Error loading tracks files: {result.errors}")
        self._tracks = result.tracks
        self._on_analyze()
