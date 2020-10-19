import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showwarning
from typing import Any, List, Optional, Protocol, Set, Union

import utils
from gui.searchablecombobox import SearchableComboBox
from track import Track
from type_hints import Parent


class OptionWidget(ttk.Frame):
    def __init__(self, parent: Parent = None) -> None:
        super().__init__(parent)

    def get_value(self) -> Any:
        pass

    def set_tracks(self, tracks: List[Track]) -> None:
        pass


class Option(Protocol):
    def __call__(self, parent: Parent = None, *, tracks: List[Track]) -> OptionWidget:
        ...


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


class ArtistChooser(OptionWidget):
    def __init__(self, parent: Parent = None):
        super().__init__(parent)

        label = ttk.Label(self, text="Artists")
        listbox_frame = ttk.Frame(self)
        self._listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED)
        vsbar = ttk.Scrollbar(listbox_frame)
        hsbar = ttk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL)

        self._combo_var = tk.StringVar()
        self._combo_box = SearchableComboBox(self, textvariable=self._combo_var)
        add_artist_button = ttk.Button(self, text="Add", command=self._on_add_artist)

        top_artists_frame = tk.Frame(self)
        top_artists_label_1 = ttk.Label(top_artists_frame, text="Top")
        self._top_artists_spinbox = ttk.Spinbox(top_artists_frame, from_=0, to=20, justify=tk.CENTER, width=1)
        top_artists_label_2 = ttk.Label(top_artists_frame, text="artists")
        top_artists_button = ttk.Button(self, text="Add", command=self._on_add_top_artists)

        label.grid(row=0, column=0, columnspan=2)
        listbox_frame.grid(row=1, column=0, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E)
        self._combo_box.grid(row=2, column=0, sticky=tk.E + tk.W)
        add_artist_button.grid(row=2, column=1, sticky=tk.N + tk.S + tk.W + tk.E)
        top_artists_frame.grid(row=3, column=0, sticky=tk.E + tk.W)
        top_artists_button.grid(row=3, column=1, sticky=tk.N + tk.S + tk.W + tk.E)

        vsbar.pack(side=tk.RIGHT, fill=tk.Y)
        hsbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._listbox.pack(expand=True, fill=tk.BOTH)

        top_artists_label_1.pack(side=tk.LEFT)
        self._top_artists_spinbox.pack(side=tk.LEFT, expand=True, fill=tk.X)
        top_artists_label_2.pack(side=tk.LEFT)

        hsbar.config(command=self._listbox.xview)
        vsbar.config(command=self._listbox.yview)
        self._listbox.config(xscrollcommand=hsbar.set)
        self._listbox.config(yscrollcommand=vsbar.set)
        self._listbox.bind("<Delete>", self._on_delete)
        self._top_artists_spinbox.set(10)

        tk.Grid.rowconfigure(self, 1, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)

        self._artists: Set[str] = set()
        self._top_artists: List[str] = []

    def get_value(self) -> List[str]:
        return self._listbox.get(0, tk.END)

    def set_tracks(self, tracks: List[Track]) -> None:
        self._artists = {track.artist for track in tracks}
        self._top_artists = [
            item[0]
            for item in sorted(
                {artist: max(listens) for artist, listens in utils.listens_per_day(tracks)[1].items()}.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]
        self._listbox.delete(0, tk.END)
        self._configure_combo_box()

    def _on_add_top_artists(self) -> None:
        self._listbox.insert(self._listbox.size(), *self._top_artists[: int(self._top_artists_spinbox.get())])

    def _on_add_artist(self) -> None:
        self._listbox.insert(self._listbox.size(), self._combo_var.get())
        self._configure_combo_box()

    def _on_delete(self, event: tk.Event) -> None:
        for index in reversed(self._listbox.curselection()):
            self._listbox.delete(index)
        self._configure_combo_box()

    def _configure_combo_box(self) -> None:
        self._combo_box.config(values={artist for artist in self._artists if artist not in self.get_value()})
