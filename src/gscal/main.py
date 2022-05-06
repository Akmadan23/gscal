#!/usr/bin/env python
import gi, re, sys, toml, getopt, datetime as dt
from importlib import metadata
from os import path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def run():
    # Default configuration
    default_config = {
        "window_resizable": False,
        "sunday_first": False,
        "sunday_color": "#CC0000",
    }

    # Default config file path
    config_path = "~/.config/gscal/gscal.toml"

    try:
        # Parsing options and arguments
        opts, args = getopt.getopt(sys.argv[1:], "hvc:", ["help", "version", "config="])
    except getopt.GetoptError as e:
        print("[ERRROR]", e)
        sys.exit(2)

    # Handling options
    for o, a in opts:
        if o in ["-h", "--help"]:
            f = open(path.dirname(__file__) + "/data/help.txt", "r")
            print(f.read())
            f.close()
            sys.exit()
        elif o in ["-v", "--version"]:
            print("gscal", metadata.version("gscal"))
            sys.exit()
        elif o in ["-c", "--config"]:
            if path.isfile(path.expanduser(a)):
                config_path = a
            else:
                print(f"[WARNING] File \"{a}\" not found.")

    # Handling arguments (not supported)
    for a in args:
        print("[WARNING] Unknown argument:", a)

    try:
        # Importing settings from config file
        config = toml.load(path.expanduser(config_path))

        # For each key of the default config dict
        for i in default_config:
            # If the value type does not match the default type or if sunday_color does not match a hex color pattern it falls back to the default
            if i not in config or type(config[i]) != type(default_config[i]) or (i == "sunday_color" and re.match("^#[0-9a-fA-F]{6}$", config[i]) is None):
                config[i] = default_config[i]
    except FileNotFoundError:
        print("[WARNING] Config file not found: default configuration loaded.")
        config = default_config
    except ValueError as e:
        print(f"[WARNING] Error in the config file: {e}. Default configuration loaded.")
        config = default_config

    # Initializing main window
    win = mainWindow(config)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()

    try:
        # Launching the GTK loop
        Gtk.main()
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted by user.")

class mainWindow(Gtk.Window):
    # Class variables
    sp = 8
    day = dt.date.today().day
    month = dt.date.today().month
    year = dt.date.today().year

    def __init__(self, c):
        # Setting window title
        super().__init__(title = "Gscal")

        # Importing config as object variable
        self.config = c

        # Main frame
        vboxFrame = Gtk.Box(spacing = self.sp, orientation = 1)
        self.add(vboxFrame)
        self.set_border_width(self.sp)
        self.set_resizable(self.config["window_resizable"])

        ######## HEADER ########

        # Box containing control buttons
        hboxHeader = Gtk.Box(spacing = self.sp)
        vboxFrame.pack_start(hboxHeader, 0, 0, 0)

        # Configuring month's combo box
        monthText = Gtk.CellRendererText()
        monthList = [(dt.date(1, 1, 1) + dt.timedelta(days = i * 31)).strftime("%B").capitalize() for i in range(12)]
        monthStore = Gtk.ListStore(str)

        for m in monthList:
            monthStore.append([m])

        self.cbxMonth = Gtk.ComboBox()
        self.cbxMonth.set_model(monthStore)
        self.cbxMonth.set_active(self.month - 1)
        self.cbxMonth.pack_start(monthText, 1)
        self.cbxMonth.add_attribute(monthText, "text", 0)
        self.cbxMonth.connect("changed", self.month_changed)
        hboxHeader.pack_start(self.cbxMonth, 0, 0, 0)

        btnPrevMonth = Gtk.Button(label = "<")
        btnPrevMonth.connect("clicked", self.month_inc, -1)
        hboxHeader.pack_start(btnPrevMonth, 0, 0, 0)

        btnNextMonth = Gtk.Button(label = ">")
        btnNextMonth.connect("clicked", self.month_inc, 1)
        hboxHeader.pack_start(btnNextMonth, 0, 0, 0)

        # Configuring year's spin button
        adjYear = Gtk.Adjustment(
            value = self.year,
            lower = 1,
            upper = 9999,
            step_increment = 1
        )

        self.spnYear = Gtk.SpinButton(adjustment = adjYear, digits = 0)
        self.spnYear.connect("changed", self.year_changed)
        self.spnYear.set_numeric(1)
        hboxHeader.pack_end(self.spnYear, 0, 0, 0)

        ######## BODY ########

        vboxBody = Gtk.Box(spacing = self.sp, orientation = 1)
        vboxFrame.pack_start(vboxBody, 0, 0, 0)

        hboxRow = [Gtk.Box(spacing = self.sp) for _ in range(7)]
        self.lblDay = [[Gtk.Label() for _ in range(7)] for _ in range(7)]

        for i, row in enumerate(hboxRow):
            vboxBody.pack_start(row, 0, 0, 0)

            for j in range(7):
                if i == 0:
                    sunday = self.config["sunday_first"]
                    text = (dt.date(1, 1, 8) + dt.timedelta(days = j - sunday)).strftime("%a").capitalize()

                    if (sunday == 1 and j == 0) or (sunday == 0 and j == 6):
                        color = self.config["sunday_color"]
                        text = f"<span fgcolor = '{color}'>{text}</span>"

                    self.lblDay[i][j].set_markup(f"<b>{text}</b>")

                self.lblDay[i][j].set_size_request(40, 0)
                row.pack_start(self.lblDay[i][j], 1, 1, 0)

        # Setting month days for the first time
        self.month_changed(None)

    def month_inc(self, widget, inc):
        self.month += inc

        if self.month == 0:
            self.month = 12
            self.year -= 1
        elif self.month == 13:
            self.month = 1
            self.year += 1

        self.cbxMonth.set_active(self.month - 1)
        self.spnYear.set_value(self.year)

    def month_changed(self, widget):
        # Updates the widget only if the call comes from itself
        if widget:
            self.month = widget.get_active() + 1

        # Counter for subsequent month days and bold flag
        nxt = 1
        bold = 0

        for i in range(1, len(self.lblDay)):
            for j in range(len(self.lblDay[i])):
                # Weekday number of the first day of the selected month
                first = int(dt.date(self.year, self.month, 1).strftime("%w"))

                # monthday number of the last day of the selected month
                if self.month == 12:
                    last = (dt.date(self.year + 1, 1, 1) - dt.timedelta(days = 1)).day
                else:
                    last = (dt.date(self.year, self.month + 1, 1) - dt.timedelta(days = 1)).day

                # Setting an offset depending on the first day of the month
                if first < 2:
                    offset = -5
                else:
                    offset = 2

                # Determining each day of the month depending on row (i), column (j), offset and first day of the month
                num = j + offset - first + 7 * (i - 1) - self.config["sunday_first"]

                if num < 1:
                    num = (dt.date(self.year, self.month, 1) + dt.timedelta(days = num - 1)).day
                    fg = "gray"
                elif num > last:
                    num = nxt
                    nxt += 1
                    fg = "gray"
                else:
                    fg = "white"

                    if self.day == num and self.month == mainWindow.month:
                        bold = 1

                text = str(num).rjust(2, "0")

                if bold:
                    text = f"<b>[{text}]</b>"
                    bold = 0

                self.lblDay[i][j].set_markup(f"<span fgcolor='{fg}'>{text}</span>")

    def year_changed(self, widget):
        try:
            self.year = int(widget.get_text())
            self.month_changed(None)
        except (ValueError, OverflowError):
            print("[WARNING] Only years between 1 and 9999 are supported.")

# Run the app when launched as script
if __name__ == "__main__":
    run()
