#!/usr/bin/python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import toml
from os.path import expanduser
from datetime import date, datetime, timedelta

class mainWindow(Gtk.Window):
    # Class variables
    sp = 8
    now = datetime.now()
    day = int(now.strftime("%d"))
    month = int(now.strftime("%m"))
    year = int(now.strftime("%Y"))

    def __init__(self):
        super().__init__(title = "Simple calendar")
        self.set_border_width(self.sp)
        self.set_resizable(0)

        ######## CONFIG ########

        try:
            # Importing settings from config file
            self.config = toml.load(expanduser("~/.config/scal/scal.toml"))
            print(self.config)
        except FileNotFoundError:
            print("Config file not found.")
        except ValueError as e:
            print("Error in the config file:", e)

        # Main frame
        vboxFrame = Gtk.Box(spacing = self.sp, orientation = 1)
        self.add(vboxFrame)

        ######## HEADER ########

        # Box containing control buttons
        hboxHeader = Gtk.Box(spacing = self.sp)
        vboxFrame.pack_start(hboxHeader, 0, 0, 0)

        # Configuring month's combo box
        monthText = Gtk.CellRendererText()
        monthList = [(date(1, 1, 1) + timedelta(days = i * 31)).strftime("%B").capitalize() for i in range(12)]
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
        self.spnYear.connect("changed", self.year_changed, 0)
        self.spnYear.set_numeric(1)
        hboxHeader.pack_end(self.spnYear, 0, 0, 0)

        ######## BODY ########

        vboxBody = Gtk.Box(spacing = self.sp, orientation = 1)
        vboxFrame.pack_start(vboxBody, 0, 0, 0)

        hboxRow = [Gtk.Box(spacing = self.sp) for i in range(7)]
        self.lblDay = [[Gtk.Label() for i in range(7)] for i in range(7)]

        for i, row in enumerate(hboxRow):
            vboxBody.pack_start(row, 0, 0, 0)

            for j in range(7):
                if i == 0:
                    text = (date(1, 1, 1) + timedelta(days = j)).strftime("%a").capitalize()
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

        self.spnYear.set_value(self.year)
        self.cbxMonth.set_active(self.month - 1)

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
                first = int(date(self.year, self.month, 1).strftime("%w"))

                # monthday number of the last day of the selected month
                if self.month == 12:
                    last = int((date(self.year + 1, 1, 1) - timedelta(days = 1)).strftime("%d"))
                else:
                    last = int((date(self.year, self.month + 1, 1) - timedelta(days = 1)).strftime("%d"))

                # Setting an offset depending on the first day of the month
                if first < 2:
                    offset = -5
                else:
                    offset = 2

                # Determining each day of the month depending on row (i), column (j), offset and first day of the month
                num = j + offset - first + 7 * (i - 1)

                if num < 1:
                    num = (date(self.year, self.month, 1) + timedelta(days = num - 1)).strftime("%d")
                    fg = "gray"
                elif num > last:
                    num = nxt
                    nxt += 1
                    fg = "gray"
                else:
                    if self.day == num:
                        bold = 1
                    fg = "white"

                text = str(num).rjust(2, "0")

                if bold:
                    text = f"<b>{text}</b>"
                    bold = 0

                self.lblDay[i][j].set_markup(f"<span fgcolor='{fg}'>{text}</span>")

    def year_changed(self, widget, inc):
        try:
            self.year = int(widget.get_text())
            self.month_changed(None)
        except ValueError:
            print("ERROR: Only years between 1 and 9999 are supported.")

try:
    win = mainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
except KeyboardInterrupt:
    print("Interrupted by user.")
