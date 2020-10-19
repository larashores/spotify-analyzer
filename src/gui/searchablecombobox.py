import contextlib
import tkinter as tk
from tkinter import ttk
from typing import Iterable, List, Optional

from type_hints import Parent


class SearchableComboBox(ttk.Frame):
    def __init__(
        self,
        parent: Parent = None,
        *,
        textvariable: Optional[tk.Variable] = None,
        values: Optional[Iterable[str]] = None,
    ):
        super().__init__(parent)
        self._entry = ttk.Entry(
            self,
            justify=tk.CENTER,
            validate="key",
            validatecommand=(self.register(self._on_type), "%d", "%i", "%S", "%P"),
            textvariable=textvariable,  # type: ignore
        )
        self._entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._entry.bind("<Return>", self._on_return)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self.winfo_toplevel().bind("<Button-1>", self._on_root_click)
        self.winfo_toplevel().bind("<Configure>", self._on_configure)

        self._toplevel: Optional[tk.Toplevel] = None
        self._listbox: Optional[tk.Listbox] = None
        self._scrollbar: Optional[ttk.Scrollbar] = None

        self._values: List[str] = []
        self._suggested: Optional[str] = None
        self.config(values=values)

        self._skip_validation = False

    def config(self, **kwargs) -> None:  # type: ignore
        if "values" in kwargs:
            values = kwargs.pop("values")

            self._values = sorted(values) if values is not None else []
            self._suggested = self._values[0] if values is not None else None
            self._listbox_configure()

            if values:
                with self._validation_disabled():
                    self._entry.insert(0, self._suggested)

        super().config(**kwargs)

    def _on_type(self, op: str, ind: str, edit: str, after: str) -> bool:
        if self._skip_validation:
            return True
        if op == "1":
            self._entry.insert(tk.INSERT, edit)
        elif op == "0":
            self._entry.delete(ind, int(ind) + len(edit))

        if not self._toplevel:
            self._popup()
        self._listbox_configure()

        if op == "1" and self._suggested:
            self._entry.insert(tk.INSERT, self._suggested[len(after) :])
            self._entry.icursor(len(after))
            self._entry.select_range(tk.INSERT, tk.END)

        return False

    def _on_root_click(self, event: tk.Event) -> None:
        if self.winfo_containing(event.x_root, event.y_root) == self._entry:
            if not self._toplevel:
                self._popup()
            self._listbox_configure()
        elif self._toplevel:
            if self._suggested:
                self._select_suggested()
            else:
                self._unpopup()

    def _on_listbox_click(self, _event: tk.Event) -> None:
        selected = self._listbox.curselection()  # type: ignore
        self._suggested = selected and self._values[selected[0]]
        self._select_suggested()

    def _on_configure(self, _event: tk.Event) -> None:
        if self._toplevel:
            self._unpopup()

    def _on_return(self, _event: tk.Event) -> None:
        if self._suggested:
            self._select_suggested()

    def _on_focus_out(self, _event: tk.Event) -> None:
        x, y =  self.winfo_pointerxy()
        if self._toplevel:
            root_x = self._toplevel.winfo_rootx()
            root_y = self._toplevel.winfo_rooty()
            if (
                root_x < x < root_x + self._toplevel.winfo_width()
                and root_y < y < root_y + self._toplevel.winfo_width()
            ):
                return  # Clicked on listbox
        if self._suggested:
            self._select_suggested()

    def _select_suggested(self) -> None:
        with self._validation_disabled():
            self._entry.delete(0, tk.END)
            self._entry.insert(0, self._suggested)
        if self._toplevel:
            self._unpopup()

    def _listbox_configure(self) -> None:
        if self._toplevel:
            self._listbox.select_clear(0, tk.END)  # type: ignore
            try:
                ind, self._suggested = next(
                    (ind, val)
                    for ind, val in enumerate(self._values)
                    if val.lower().startswith(self._entry.get().lower())
                )
            except StopIteration:
                self._suggested = None
            else:
                self._listbox.see(ind)  # type: ignore
                self._listbox.select_set((ind,))  # type: ignore

    def _popup(self) -> None:
        assert not self._toplevel
        if not self._values:
            return
        self._toplevel = tk.Toplevel(self)
        self._toplevel.overrideredirect(True)
        self._toplevel.geometry(f"+{self._entry.winfo_rootx()}+{self._entry.winfo_rooty()+self._entry.winfo_height()}")
        self._listbox = tk.Listbox(
            self._toplevel, selectmode=tk.SINGLE, height=min(len(self._values), 10), exportselection=False
        )
        self._listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._listbox.bind("<Button-1>", lambda event: self.after(20, self._on_listbox_click, event))  # type: ignore
        self._listbox.insert(0, *self._values)  # ignore

        if len(self._values) > 10:
            self._scrollbar = ttk.Scrollbar(self._toplevel, orient=tk.VERTICAL, command=self._listbox.yview)
            self._scrollbar.pack(expand=True, fill=tk.Y)
            self._listbox.config(yscrollcommand=self._scrollbar.set)

    def _unpopup(self) -> None:
        assert self._toplevel
        self._toplevel.destroy()
        self._toplevel = None
        self._listbox = None

    @contextlib.contextmanager
    def _validation_disabled(self):
        try:
            self._skip_validation = True
            yield
        finally:
            self._skip_validation = False
