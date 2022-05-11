import gi, datetime as dt, calendar as cal

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
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

        # Box containing month and year controls
        hboxHeader = Gtk.Box(spacing = self.sp)
        vboxFrame.pack_start(hboxHeader, 0, 0, 0)

        # Configuring month's combo box
        monthText = Gtk.CellRendererText()
        monthStore = Gtk.ListStore(str)

        for m in cal.month_name[1:]:
            monthStore.append([m.capitalize()])

        # Month combo box
        self.cbxMonth = Gtk.ComboBox()
        self.cbxMonth.set_model(monthStore)
        self.cbxMonth.set_active(self.month - 1)
        self.cbxMonth.pack_start(monthText, 1)
        self.cbxMonth.add_attribute(monthText, "text", 0)
        self.cbxMonth.connect("changed", self.month_changed)
        hboxHeader.pack_start(self.cbxMonth, 0, 0, 0)

        # Configuring year's spin button
        adjYear = Gtk.Adjustment(
            value = self.year,
            lower = 1,
            upper = 9999,
            step_increment = 1
        )

        # Year spin button
        self.spnYear = Gtk.SpinButton(adjustment = adjYear, digits = 0)
        self.spnYear.connect("changed", self.year_changed)
        self.spnYear.set_numeric(1)
        hboxHeader.pack_end(self.spnYear, 0, 0, 0)

        ######## BODY ########

        # Grid containing each day of the current month
        self.gridBody = Gtk.Grid(row_spacing = self.sp, column_spacing = self.sp)
        vboxFrame.pack_start(self.gridBody, 1, 1, 0)

        for row in range(7):
            for col in range(7):
                lblDay = Gtk.Label()

                if row == 0:
                    sunday = self.config["sunday_first"]
                    text = cal.day_abbr[col - sunday].capitalize()

                    if (sunday == 1 and col == 0) or (sunday == 0 and col == 6):
                        color = self.config["sunday_color"]
                        text = f"<span fgcolor = '{color}'>{text}</span>"

                    lblDay.set_markup(f"<b>{text}</b>")

                lblDay.set_size_request(40, 0)
                self.gridBody.attach(lblDay, col, row, 1, 1)

        ######## FOOTER ########

        # Bottom box containing previous and next month buttons
        hboxFooter = Gtk.Box(spacing = self.sp)
        vboxFrame.pack_start(hboxFooter, 0, 0, 0)

        # Previous month button
        self.btnPrevMonth = Gtk.Button()
        self.btnPrevMonth.set_size_request(120, 0)
        self.btnPrevMonth.connect("clicked", self.month_inc, -1)
        hboxFooter.pack_start(self.btnPrevMonth, 1, 1, 0)

        # Next month button
        self.btnNextMonth = Gtk.Button()
        self.btnNextMonth.set_size_request(120, 0)
        self.btnNextMonth.connect("clicked", self.month_inc, 1)
        hboxFooter.pack_start(self.btnNextMonth, 1, 1, 0)

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
        # Updating the widget only if the call comes from itself
        if widget:
            self.month = widget.get_active() + 1

        # Updating prev and next month buttons
        self.btnPrevMonth.set_label("\u25C0  " + cal.month_name[self.month - 1 or 12].capitalize())
        self.btnNextMonth.set_label(cal.month_name[self.month - 12 or 1].capitalize() + "  \u25B6")

        # Counter for subsequent month days and bold flag
        nxt = 1
        bold = 0

        for row in range(1, 7):
            for col in range(7):
                # Weekday number of the first day of the selected month
                first = cal.weekday(self.year, self.month, 1) or 7

                # monthday number of the last day of the selected month
                if self.month == 12:
                    last = (dt.date(self.year + 1, 1, 1) - dt.timedelta(days = 1)).day
                else:
                    last = (dt.date(self.year, self.month + 1, 1) - dt.timedelta(days = 1)).day

                # Determining each day of the month depending on row, column, offset and first day of the month
                num = 1 + col - first + 7 * (row - 1) - self.config["sunday_first"]

                if num < 1:
                    num = (dt.date(self.year, self.month, 1) + dt.timedelta(days = num - 1)).day
                    fg = "gray"
                elif num > last:
                    num = nxt
                    nxt += 1
                    fg = "gray"
                else:
                    fg = "white"

                    if self.day == num and self.month == MainWindow.month and self.year == MainWindow.year:
                        bold = 1

                text = str(num).rjust(2, "0")

                if bold:
                    text = f"<b>[{text}]</b>"
                    bold = 0

                lblDay = self.gridBody.get_child_at(col, row)
                lblDay.set_markup(f"<span fgcolor='{fg}'>{text}</span>")

    def year_changed(self, widget):
        try:
            self.year = int(widget.get_text())
            self.month_changed(None)
        except (ValueError, OverflowError):
            print("[WARNING] Only years between 1 and 9999 are supported.")
