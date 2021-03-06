import colorsys
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, List, Optional, Protocol, Set

from matplotlib.colors import ListedColormap

import utils
from gui.searchablecombobox import SearchableComboBox
from track import Track
from type_hints import Parent


def _hue_colormap(hue: float) -> ListedColormap:
    return ListedColormap([colorsys.hsv_to_rgb(hue, saturation / 255, 1) for saturation in range(255)])


class OptionWidget(ttk.Frame):
    def get_value(self) -> Any:
        pass

    def set_tracks(self, tracks: List[Track]) -> None:
        pass


class Option(Protocol):
    def __call__(self, parent: Parent = None) -> OptionWidget:
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


class _Spinbox(OptionWidget):
    def __init__(self, parent: Parent, *, text: str, from_: int, to: int, default: int):
        super().__init__(parent)
        self._var = tk.StringVar(self)
        label = ttk.Label(self, text=text)
        spinbox = ttk.Spinbox(self, from_=from_, to=to, width=5, textvariable=self._var, justify=tk.CENTER)

        label.pack(side=tk.LEFT)
        spinbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        spinbox.set(default)

    def get_value(self) -> int:
        return int(self._var.get())


class Spinbox:
    def __init__(self, *, text: str, from_: int, to: int, default: int):
        self._text = text
        self._from = from_
        self._to = to
        self._default = default

    def __call__(self, parent: Parent = None) -> OptionWidget:
        return _Spinbox(parent, text=self._text, from_=self._from, to=self._to, default=self._default)


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
        self._combo_var.set("")
        self._configure_combo_box()

    def _on_delete(self, _event: tk.Event) -> None:
        for index in reversed(self._listbox.curselection()):
            self._listbox.delete(index)
        self._configure_combo_box()

    def _configure_combo_box(self) -> None:
        self._combo_box.config(values={artist for artist in self._artists if artist not in self.get_value()})


class HueChooser(ttk.Frame):
    def __init__(
        self, parent: Parent = None, *, samples: int = 5, hue: float = 0.0, command: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        scale_frame = ttk.Frame(self)
        label = ttk.Label(scale_frame, text="Color")
        scale = ttk.Scale(scale_frame, command=self._on_scale_move, value=hue)
        frame_frame = ttk.Frame(self)
        self._frames = [tk.Frame(frame_frame, width=50, height=50) for color in range(samples)]
        self._accept_button = ttk.Button(self, text="Okay", command=command)

        scale_frame.pack(expand=True, fill=tk.X)
        label.pack(side=tk.LEFT)
        scale.pack(side=tk.LEFT, expand=True, fill=tk.X)

        frame_frame.pack(expand=True, fill=tk.BOTH)
        for frame in self._frames:
            frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self._accept_button.pack()
        self._set_hue(hue)

    def config(self, **kwargs) -> None:
        if "command" in kwargs:
            command = kwargs.pop("command")
            self._accept_button.config(command=command)
        super().config(**kwargs)

    @property
    def hue(self) -> float:
        return self._hue

    def _on_scale_move(self, hue: str) -> None:
        self._set_hue(float(hue))

    def _set_hue(self, hue: float) -> None:
        self._hue = hue
        self._color_map = _hue_colormap(hue)
        for ind, frame in enumerate(self._frames):
            color = [round(i * 255) for i in self._color_map.colors[ind * self._color_map.N // len(self._frames)]]
            frame.config(background=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")


def ask_hue(parent: Parent = None, *, hue: float = 0.0) -> float:
    toplevel = tk.Toplevel(parent)
    chooser = HueChooser(toplevel, hue=hue)

    class AcceptCommand:
        def __init__(self):
            self.hue = None

        def __call__(self):
            toplevel.destroy()
            self.hue = chooser.hue

    command = AcceptCommand()
    toplevel.protocol("WM_DELETE_WINDOW", command)
    chooser.config(command=command)
    chooser.pack(expand=True, fill=tk.BOTH)
    toplevel.wait_window()
    return command.hue


class ColorMap(OptionWidget):
    def __init__(self, parent: Parent = None):
        super().__init__(parent)

        button = ttk.Label(self, text="Color: ")
        self._color_frame = tk.Frame(self, relief="ridge")

        button.pack(side=tk.LEFT)
        self._color_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(5, 0), pady=2)

        self._color_frame.bind("<Button-1>", self._on_click)

        self._hue = 240 / 360
        self._color_map = _hue_colormap(self._hue)
        self._set_color()

    def get_value(self) -> ListedColormap:
        return self._color_map

    def _on_click(self, event: tk.Event) -> None:
        if (hue := ask_hue(hue=self._hue)) is not None:
            self._hue = hue
            self._color_map = _hue_colormap(self._hue)
            self._set_color()

    def _set_color(self) -> None:
        color = [round(i * 255) for i in self._color_map.colors[-1]]
        self._color_frame.config(background=f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}")
