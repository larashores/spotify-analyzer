"""
Simple calendar using ttk Treeview together with calendar and datetime
classes.
"""
import calendar
import datetime
import tkinter as tk
import tkinter.font
from tkinter import ttk
from tkinter.messagebox import showwarning


def get_calendar(locale, fwday):
    # instantiate proper calendar class
    if locale is None:
        return calendar.TextCalendar(fwday)
    else:
        return calendar.LocaleTextCalendar(fwday, locale)


class Calendar(ttk.Frame):
    # XXX ToDo: cget and configure

    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta

    def __init__(self, master=None, **kw):
        """
        WIDGET-SPECIFIC OPTIONS

            locale, firstweekday, year, month, selectbackground,
            selectforeground
        """
        # remove custom options from kw before initializating ttk.Frame
        fwday = kw.pop("firstweekday", calendar.MONDAY)
        year = kw.pop("year", self.datetime.now().year)
        month = kw.pop("month", self.datetime.now().month)
        day = kw.pop("month", self.datetime.now().day)
        locale = kw.pop("locale", None)
        sel_bg = kw.pop("selectbackground", "#ecffc4")
        sel_fg = kw.pop("selectforeground", "#05640e")

        self._date = self.datetime(year, month, day)
        self._selection = None  # no date selected

        ttk.Frame.__init__(self, master, **kw)

        self._cal = get_calendar(locale, fwday)

        self.__setup_styles()  # creates custom styles
        self.__place_widgets()  # pack/grid used widgets
        self.__config_calendar()  # adjust calendar columns and setup tags
        # configure a canvas, and proper bindings, for selecting dates
        self.__setup_selection(sel_bg, sel_fg)

        # store items ids, used for insertion later
        self._items = [self._calendar.insert("", "end", values="") for _ in range(6)]
        # insert dates in the currently empty calendar
        self._build_calendar()

        # set the minimal size for the widget
        # self._calendar.bind('<Map>', self.__minsize)

    def __setitem__(self, item, value):
        if item in ("year", "month"):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == "selectbackground":
            self._canvas["background"] = value
        elif item == "selectforeground":
            self._canvas.itemconfigure(self._canvas.text, item=value)
        else:
            ttk.Frame.__setitem__(self, item, value)

    def __getitem__(self, item):
        if item in ("year", "month"):
            return getattr(self._date, item)
        elif item == "selectbackground":
            return self._canvas["background"]
        elif item == "selectforeground":
            return self._canvas.itemcget(self._canvas.text, "fill")
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(self, item)})
            return r[item]

    def __setup_styles(self):
        def arrow_layout(direction):
            return [("Button.focus", {"children": [(f"Button.{direction}arrow", None)]})]

        # custom ttk styles
        style = ttk.Style(self.master)
        style.layout("L.TButton", arrow_layout("left"))
        style.layout("R.TButton", arrow_layout("right"))
        style.layout("U.TButton", arrow_layout("up"))
        style.layout("D.TButton", arrow_layout("down"))

    def __place_widgets(self):
        # header frame and its widgets
        hframe = ttk.Frame(self)
        lbtn = ttk.Button(hframe, style="L.TButton", command=self._prev_month)
        rbtn = ttk.Button(hframe, style="R.TButton", command=self._next_month)
        self._header = ttk.Label(hframe, width=15, anchor="center")
        # the calendar
        self._calendar = ttk.Treeview(self, show="", selectmode="none", height=7)

        # pack the widgets
        hframe.pack(in_=self, side="top", pady=4, anchor="center")
        lbtn.grid(in_=hframe)
        self._header.grid(in_=hframe, column=1, row=0, padx=12)
        rbtn.grid(in_=hframe, column=2, row=0)
        self._calendar.pack(in_=self, expand=1, fill="both", side="bottom")

    def __config_calendar(self):
        cols = self._cal.formatweekheader(3).split()
        self._calendar["columns"] = cols
        self._calendar.tag_configure("header", background="grey90")
        self._calendar.insert("", "end", values=cols, tag="header")
        # adjust its columns width
        font = tk.font.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            self._calendar.column(col, width=maxwidth, minwidth=maxwidth, anchor="e")

    def __setup_selection(self, sel_bg, sel_fg):
        self._font = tk.font.Font()
        self._canvas = canvas = tk.Canvas(self._calendar, background=sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor="w")

        canvas.bind("<ButtonPress-1>", lambda evt: canvas.place_forget())
        self._calendar.bind("<Configure>", lambda evt: canvas.place_forget())
        self._calendar.bind("<ButtonPress-1>", self._pressed)

    # def __minsize(self, evt):
    #    width, height = self._calendar.master.geometry().split('x')
    #    height = height[:height.index('+')]
    #    self._calendar.master.minsize(width, height)

    def _build_calendar(self):
        year, month = self._date.year, self._date.month

        # update header text (Month, YEAR)
        header = self._cal.formatmonthname(year, month, 0)
        self._header["text"] = header.title()

        # update calendar shown dates
        cal = self._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(self._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [("%02d" % day) if day else "" for day in week]
            self._calendar.item(item, values=fmt_week)

    def _show_selection(self, text, bbox):
        """Configure canvas for a new selection."""
        x, y, width, height = bbox

        textw = self._font.measure(text)

        canvas = self._canvas
        canvas.configure(width=width, height=height)
        canvas.coords(canvas.text, width - textw, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)

    # Callbacks

    def _pressed(self, evt):
        """Clicked somewhere in the calendar."""
        x, y, widget = evt.x, evt.y, evt.widget
        item = widget.identify_row(y)
        column = widget.identify_column(x)

        if not column or item not in self._items:
            # clicked in the weekdays row or just outside the columns
            return

        item_values = widget.item(item)["values"]
        if not len(item_values):  # row is empty for this month
            return

        text = item_values[int(column[1]) - 1]
        if not text:  # date is empty
            return

        bbox = widget.bbox(item, column)
        if not bbox:  # calendar not visible yet
            return

        # update and then show selection
        text = "%02d" % text
        self._selection = (text, item, column)
        self._show_selection(text, bbox)

    def _prev_month(self):
        """Updated calendar to show the previous month."""
        self._canvas.place_forget()

        self._date = self._date - self.timedelta(days=1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar()  # reconstuct calendar

    def _next_month(self):
        """Update calendar to show the next month."""
        self._canvas.place_forget()

        year, month = self._date.year, self._date.month
        self._date = self._date + self.timedelta(days=calendar.monthrange(year, month)[1] + 1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar()  # reconstruct calendar

    # Properties

    @property
    def selection(self):
        """Return a datetime representing the current selected date."""
        if not self._selection:
            return None

        year, month = self._date.year, self._date.month
        return self.datetime(year, month, int(self._selection[0]))


class Time(ttk.Frame):
    TIME_STRING = "{}:{:02} {}"

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.setup_styles()
        self.hour = tk.IntVar()
        self.minute = tk.IntVar()
        self.suffix = None

        self.display = ttk.Label(self)
        # sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.update_time()
        self.amPmFrame = ttk.Frame(self)
        self.am = ttk.Label(self.amPmFrame, text=" am ")
        self.div = ttk.Label(self.amPmFrame, text="|")
        self.pm = ttk.Label(self.amPmFrame, text=" pm ")
        self.pickerFrame = ttk.Frame(self)

        self.hourFrame = ttk.Frame(self.pickerFrame)
        self.hourScale = ttk.Scale(
            self.hourFrame,
            variable=self.hour,
            orient=tk.VERTICAL,
            from_=0,
            to=11,
            command=lambda val_str: self.on_move(self.hour, val_str),
        )

        self.minFrame = ttk.Frame(self.pickerFrame)
        self.minScale = ttk.Scale(
            self.minFrame,
            variable=self.minute,
            orient=tk.VERTICAL,
            from_=0,
            to=59,
            command=lambda val_str: self.on_move(self.minute, val_str),
        )

        self.display.pack()
        # sep.pack(fill=tk.X, padx=10, pady=(3, 0))
        self.amPmFrame.pack()
        self.am.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.div.pack(side=tk.LEFT)
        self.pm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.pickerFrame.pack(expand=tk.YES, fill=tk.BOTH)
        self.hourFrame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.Y)
        self.minFrame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.Y)

        ttk.Label(self.hourFrame, text="Hour").pack()
        self.hourScale.pack(expand=tk.YES, fill=tk.Y)
        ttk.Label(self.minFrame, text="Minute").pack()
        self.minScale.pack(expand=tk.YES, fill=tk.Y)

        self.on_am(None)

        self.am.bind("<Button-1>", self.on_am)
        self.pm.bind("<Button-1>", self.on_pm)

    def on_am(self, _event):
        self.suffix = "am"
        self.am.state(["selected"])
        self.pm.state(["!selected"])
        self.update_time()

    def on_pm(self, _event):
        self.suffix = "pm"
        self.am.state(["!selected"])
        self.pm.state(["selected"])
        self.update_time()

    def get_hour(self):
        hour = self.hour.get()
        return 12 if hour == 0 else hour

    def update_time(self):
        hour = self.get_hour()
        self.display.config(text=self.TIME_STRING.format(hour, self.minute.get(), self.suffix))

    def on_move(self, var, val_str):
        var.set(round(float(val_str), 0))
        self.update_time()

    def setup_styles(self):
        # custom ttk styles
        style = ttk.Style(self.master)
        style.map("TLabel", foreground=[("selected", "blue")], font=[("selected", ("TkDefaultFont", 10, "bold"))])

    def get_time(self):
        hour = self.hour.get()
        twenty_four_hour = hour if self.suffix == "am" else hour + 12
        return datetime.time(twenty_four_hour, self.minute.get())


class DateTime(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.calendar = Calendar(self, firstweekday=calendar.SUNDAY)
        self.timePicker = Time(self)

        self.calendar.pack(side=tk.LEFT, expand=tk.YES, fill=tk.X)
        self.timePicker.pack(side=tk.LEFT)

    def selection(self):
        date = self.calendar.selection
        if date is None:
            return None
        time = self.timePicker.get_time()
        return datetime.datetime(date.year, date.month, date.day, time.hour, time.minute)

    def end(self):
        if self.selection() is None:
            showwarning(title="Warning", message="Please select a date")
            return
        self.quit()


def get_datetime(parent):
    dialog = tk.Toplevel(parent)
    win = DateTime(dialog)
    dialog.wm_title("Select Date and Time")
    dialog.wm_protocol("WM_DELETE_WINDOW", win.quit)
    win.pack(expand=tk.YES, fill=tk.BOTH)
    ttk.Button(dialog, text="Okay", command=win.end).pack()
    dialog.update()
    dialog.minsize(dialog.winfo_reqwidth(), dialog.winfo_reqheight())
    dialog.focus_get()
    dialog.focus_set()
    dialog.grab_set()
    dialog.transient(parent)
    win.mainloop()
    dt = win.selection()
    dialog.destroy()
    return dt


def test1():
    import sys

    root = tk.Tk()
    root.title("Ttk Calendar")
    ttkcal = Calendar(firstweekday=calendar.SUNDAY)
    ttkcal.pack(expand=1, fill="both")

    if "win" not in sys.platform:
        style = ttk.Style()
        style.theme_use("clam")

    root.mainloop()


def test2():
    root = tk.Tk()
    win = Time(root)
    win.pack(expand=tk.YES, fill=tk.BOTH)
    root.mainloop()


def test3():
    root = tk.Tk()
    win = DateTime(root)
    win.pack(expand=tk.YES, fill=tk.BOTH)
    root.mainloop()


def test4():
    root = tk.Tk()
    ttk.Button(root, text="button", command=lambda: print(get_datetime(root))).pack()
    root.mainloop()


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
