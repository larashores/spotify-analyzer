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
            textvariable=textvariable,
        )
        self._entry.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._entry.bind("<Return>", self._on_return)
        self._entry.bind("<FocusOut>", self._on_focus_out)
        self.winfo_toplevel().bind("<Button-1>", self._on_root_click)
        self.winfo_toplevel().bind("<Configure>", self._on_configure)

        self._toplevel: Optional[tk.Toplevel] = None
        self._listbox: Optional[tk.Listbox] = None
        self._scrollbar: Optional[ttk.Scrollbar] = None

        self._values: List[str]
        self._suggestions: List[str]
        self.config(values=values)

    def _on_type(self, op: str, ind: str, edit: str, after: str) -> bool:
        if op == "1":
            self._entry.insert(tk.INSERT, edit)
        elif op == "0":
            self._entry.delete(ind, int(ind) + len(edit))

        if not self._toplevel:
            self._popup()
        self._listbox_configure()

        if op == "1" and self._suggestions:
            self._entry.insert(tk.INSERT, self._suggestions[0][len(after) :])
            self._entry.icursor(len(after))
            self._entry.select_range(tk.INSERT, tk.END)

        return False

    def _on_root_click(self, event: tk.Event) -> None:
        if self.winfo_containing(event.x_root, event.y_root) == self._entry:
            if not self._toplevel:
                self._popup()
            self._listbox_configure()
        elif self._toplevel:
            self._unpopup()

    def _on_listbox_click(self, event: tk.Event) -> None:
        self._select_suggestion()

    def _on_configure(self, event: tk.Event) -> None:
        if self._toplevel:
            self._unpopup()

    def _on_return(self, event: tk.Event) -> None:
        self._select_suggestion()

    def _on_focus_out(self, event: tk.Event) -> None:
        value = self._entry.get().lower()
        if value not in self._values:
            new = self._suggestions[0] if self._suggestions else self._values[0] if self._values else ""
            self._entry.delete(0, tk.END)
            self._entry.insert(0, new)

    def _select_suggestion(self) -> None:
        selection = self._suggestions[self._listbox.curselection()[0]]
        self._entry.delete(0, tk.END)
        self._entry.insert(0, selection)
        self._unpopup()

    def _listbox_configure(self) -> None:
        self._suggestions = sorted(val for val in self._values if val.lower().startswith(self._entry.get().lower()))
        if self._toplevel:
            if not self._suggestions:
                self._unpopup()
            else:
                size = len(self._suggestions)
                if size > 10:
                    size = 10
                    if not self._scrollbar:
                        self._scrollbar = ttk.Scrollbar(self._toplevel, orient=tk.VERTICAL)
                        self._scrollbar.pack(expand=True, fill=tk.Y)
                        self._scrollbar.config(command=self._listbox.yview)
                        self._listbox.config(yscrollcommand=self._scrollbar.set)
                elif self._scrollbar:
                    self._listbox.config(yscrollcommand=None)
                    self._scrollbar.destroy()
                    self._scrollbar = None
                self._listbox.configure(height=size)
                self._listbox.delete(0, tk.END)
                self._listbox.insert(0, *self._suggestions)
                self._listbox.select_set((0))

    def _popup(self) -> None:
        assert not self._toplevel
        self._toplevel = tk.Toplevel(self)
        self._toplevel.overrideredirect(True)
        self._toplevel.geometry(f"+{self._entry.winfo_rootx()}+{self._entry.winfo_rooty()+self._entry.winfo_height()}")
        self._listbox = tk.Listbox(self._toplevel, selectmode=tk.SINGLE)
        self._listbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self._listbox.bind("<Button-1>", lambda event: self.after(20, self._on_listbox_click, event))

    def _unpopup(self) -> None:
        self._toplevel.destroy()
        self._toplevel = None
        self._listbox = None

    def config(self, **kwargs) -> None:
        if "values" in kwargs:
            values = kwargs.pop("values")

            self._values = list(values) if values is not None else []
            self._listbox_configure()

        super().config(**kwargs)
