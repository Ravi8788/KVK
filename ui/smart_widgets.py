"""Additional office screens: search, quality, duplicates, import, calendar, and settings."""

import csv
from datetime import datetime

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor, QTextCharFormat, QTextDocument
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QCalendarWidget,
)

from analytics.analytics_widget import SimpleChart
from ui.loading_overlay import busy
from controllers.auth_controller import AuthController
from services.activity_service import ActivityService
from services.smart_service import (
    AnomalyService,
    DuplicateService,
    ImportService,
    InsightService,
    QualityService,
    SearchService,
    SettingsService,
)


def _page(title, subtitle=""):
    root = QVBoxLayout()
    root.setContentsMargins(8, 8, 8, 8)
    root.setSpacing(10)
    heading = QLabel(title)
    heading.setObjectName("CardTitle")
    root.addWidget(heading)
    if subtitle:
        note = QLabel(subtitle)
        note.setObjectName("SubtitleLabel")
        note.setWordWrap(True)
        root.addWidget(note)
    return root


def _table(headers):
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    return table


def _fill(table, rows):
    table.setRowCount(0)
    for row_index, values in enumerate(rows):
        table.insertRow(row_index)
        for column, value in enumerate(values):
            table.setItem(row_index, column, QTableWidgetItem("" if value is None else str(value)))


def _export_rows(parent, headers, rows, default_name):
    path, _ = QFileDialog.getSaveFileName(parent, "Save CSV", default_name, "CSV Files (*.csv)")
    if not path:
        return
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)
    QMessageBox.information(parent, "Exported", f"Saved to:\n{path}")


def _print_html(parent, title, html):
    printer = QPrinter(QPrinter.HighResolution)
    printer.setDocName(title)
    dialog = QPrintDialog(printer, parent)
    if dialog.exec_() != QDialog.Accepted:
        return
    document = QTextDocument()
    document.setHtml(html)
    document.print_(printer)


class SearchDialog(QDialog):
    def __init__(self, text, open_module, parent=None):
        super().__init__(parent)
        self.open_module = open_module
        self.setWindowTitle("Search")
        self.resize(860, 520)
        self.results = []
        layout = QVBoxLayout(self)
        self.query = QLineEdit(text)
        self.query.setPlaceholderText("Farmer name, ID number such as 48, mobile, village, OFT, FLD, training")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._run)
        row = QHBoxLayout()
        row.addWidget(self.query, 1)
        row.addWidget(search_btn)
        layout.addLayout(row)
        self.table = _table(["Type", "Title", "Date", "Identifier", "Village"])
        self.table.cellDoubleClicked.connect(self._open_current)
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        open_btn = QPushButton("Open record")
        print_btn = QPushButton("Print")
        print_btn.setObjectName("SecondaryButton")
        open_btn.clicked.connect(self._open_current)
        print_btn.clicked.connect(self._print_current)
        buttons.addWidget(open_btn)
        buttons.addWidget(print_btn)
        buttons.addStretch(1)
        layout.addLayout(buttons)
        self._run()

    def _run(self):
        with busy(self, "Searching"):
            self.results = SearchService.search(self.query.text())
        _fill(
            self.table,
            [
                [row["record_type"], row["title"], row["activity_date"], row["identifier"], row["village"]]
                for row in self.results
            ],
        )
        if not self.results:
            QMessageBox.information(self, "Search", "No matching records.")

    def _current(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.results):
            QMessageBox.information(self, "Search", "Select a result first.")
            return None
        return self.results[row]

    def _open_current(self, *_args):
        row = self._current()
        if row is None:
            return
        detail = (
            f"<h2>{row['title']}</h2>"
            f"<p><b>Type:</b> {row['record_type']}<br>"
            f"<b>Farmer ID:</b> {row['farmer_code']}<br>"
            f"<b>Farmer:</b> {row['farmer_name']}<br>"
            f"<b>Village:</b> {row['village']}<br>"
            f"<b>Mobile:</b> {row['contact_number']}<br>"
            f"<b>Date:</b> {row['activity_date']}<br>"
            f"<b>Department:</b> {row['department']}<br>"
            f"<b>Activity:</b> {row['activity_type']}</p>"
        )
        box = QMessageBox(self)
        box.setWindowTitle(row["record_type"])
        box.setTextFormat(Qt.RichText)
        box.setText(detail)
        open_button = box.addButton("Open module", QMessageBox.AcceptRole)
        box.addButton("Close", QMessageBox.RejectRole)
        box.exec_()
        if box.clickedButton() == open_button and self.open_module:
            self.open_module(row["record_type"], row.get("search_text") or row.get("farmer_code") or "")
            self.accept()

    def _print_current(self):
        row = self._current()
        if row is None:
            return
        kvk = SettingsService.get("kvk_name")
        html = (
            f"<h2>{kvk}</h2><h3>{row['record_type']}</h3>"
            f"<p>Farmer ID: {row['farmer_code']}<br>Name: {row['farmer_name']}<br>"
            f"Village: {row['village']}<br>Mobile: {row['contact_number']}<br>"
            f"Date: {row['activity_date']}<br>Department: {row['department']}<br>"
            f"Title: {row['title']}</p>"
        )
        _print_html(self, row["title"], html)


class OverviewWidget(QWidget):
    def __init__(self, open_module):
        super().__init__()
        self.open_module = open_module
        layout = _page("Overview", "Recently added and updated records, plus items that need attention.")
        self.setLayout(layout)
        refresh = QPushButton("Refresh")
        refresh.setObjectName("SecondaryButton")
        refresh.clicked.connect(self.reload)
        layout.addWidget(refresh, 0, Qt.AlignLeft)
        self.alert_table = _table(["Alert", "Detail"])
        self.added_table = _table(["Record", "Module", "When", "Farmer ID"])
        self.updated_table = _table(["Record", "Module", "When", "Farmer ID"])
        self.alert_table.cellDoubleClicked.connect(lambda _r, _c: self._open_alert())
        self.added_table.cellDoubleClicked.connect(lambda _r, _c: self._open_recent("added"))
        self.updated_table.cellDoubleClicked.connect(lambda _r, _c: self._open_recent("updated"))
        for title, table in (("Smart alerts", self.alert_table), ("Recently added", self.added_table), ("Recently updated", self.updated_table)):
            label = QLabel(title)
            label.setObjectName("CardTitle")
            layout.addWidget(label)
            layout.addWidget(table)
        self.alerts = []
        self.recent = {"added": [], "updated": []}
        self.reload()

    def reload(self):
        self.alerts = InsightService.alerts()
        self.recent = InsightService.recent()
        _fill(self.alert_table, [[row["title"], row["detail"]] for row in self.alerts] or [["No alerts", "Nothing needs attention right now."]])
        _fill(self.added_table, [[row["title"], row["module"], _stamp(row["when"]), row["identifier"]] for row in self.recent["added"]])
        _fill(self.updated_table, [[row["title"], row["module"], _stamp(row["when"]), row["identifier"]] for row in self.recent["updated"]])

    def _open_alert(self):
        row = self.alert_table.currentRow()
        if 0 <= row < len(self.alerts):
            self.open_module(self.alerts[row]["open_module"], "")

    def _open_recent(self, kind):
        row = (self.added_table if kind == "added" else self.updated_table).currentRow()
        records = self.recent[kind]
        if 0 <= row < len(records):
            self.open_module(records[row]["open_module"], records[row].get("identifier") or "")


class DataQualityWidget(QWidget):
    METRICS = [
        ("total_checked", "Total records checked"),
        ("complete", "Complete records"),
        ("incomplete", "Incomplete records"),
        ("missing_mobile", "Missing mobile"),
        ("missing_village", "Missing village"),
        ("invalid_dates", "Invalid dates"),
        ("invalid_values", "Invalid values"),
        ("possible_duplicates", "Possible duplicates"),
    ]

    def __init__(self, open_module):
        super().__init__()
        self.open_module = open_module
        self.rows = []
        layout = _page(
            "Data Quality",
            "Select a metric to list the records behind it. Click a row to open that module and show the Farmer ID.",
        )
        self.setLayout(layout)
        self.buttons = {}
        grid = QGridLayout()
        for index, (key, label) in enumerate(self.METRICS):
            button = QPushButton(label)
            button.setMinimumHeight(64)
            button.clicked.connect(lambda _checked=False, metric=key: self._show(metric))
            self.buttons[key] = button
            grid.addWidget(button, index // 4, index % 4)
        layout.addLayout(grid)
        self.table = _table(["Module", "Department", "Record", "Detail", "Farmer ID"])
        self.table.cellClicked.connect(self._open_row)
        self.table.cellDoubleClicked.connect(self._open_row)
        layout.addWidget(self.table)
        self.reload()

    def reload(self):
        summary = QualityService.summary()
        for key, label in self.METRICS:
            self.buttons[key].setText(f"{label}\n{summary.get(key, 0):,}")
        self._show("incomplete")

    def _show(self, metric):
        if metric == "total_checked":
            self.rows = []
            _fill(self.table, [])
            return
        self.rows = QualityService.records(metric)
        _fill(
            self.table,
            [
                [
                    row["module"],
                    row.get("department", ""),
                    row["title"],
                    row["detail"],
                    row["identifier"],
                ]
                for row in self.rows
            ],
        )
        if not self.rows:
            _fill(self.table, [["—", "", "No records in this group", "", ""]])

    def _open_row(self, row, _column):
        if 0 <= row < len(self.rows):
            item = self.rows[row]
            self.open_module(item["open_module"], item.get("search_text") or item.get("identifier") or "")


class DuplicateWidget(QWidget):
    def __init__(self, user, open_module):
        super().__init__()
        self.user = user
        self.open_module = open_module
        self.pairs = []
        layout = _page("Duplicate farmers", "Possible matches stay in the database until you review them. Nothing is deleted automatically.")
        self.setLayout(layout)
        refresh = QPushButton("Refresh")
        refresh.setObjectName("SecondaryButton")
        refresh.clicked.connect(self.reload)
        layout.addWidget(refresh, 0, Qt.AlignLeft)
        self.table = _table(["Record A", "Record B", "Match", "Farmer IDs"])
        layout.addWidget(self.table)
        actions = QHBoxLayout()
        for label, handler in (
            ("Review", self._review),
            ("Keep both", self._keep),
            ("Correct record", self._correct),
            ("Merge", self._merge),
        ):
            button = QPushButton(label)
            if label != "Review":
                button.setObjectName("SecondaryButton")
            button.clicked.connect(handler)
            actions.addWidget(button)
        actions.addStretch(1)
        layout.addLayout(actions)
        self.reload()

    def reload(self):
        self.pairs = DuplicateService.find_pairs()
        _fill(
            self.table,
            [[f"{row['left_name']} ({row['left_village']})", f"{row['right_name']} ({row['right_village']})", row["reason"], f"{row['left_code']} · {row['right_code']}"] for row in self.pairs],
        )
        if not self.pairs:
            _fill(self.table, [["No possible duplicates", "", "", ""]])

    def _selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.pairs):
            QMessageBox.information(self, "Duplicates", "Select a pair first.")
            return None
        return self.pairs[row]

    def _review(self):
        pair = self._selected()
        if pair is None:
            return
        QMessageBox.information(
            self,
            "Possible duplicate",
            f"Record A\n{pair['left_code']}  {pair['left_name']}\n{pair['left_village']}  {pair['left_mobile']}\n\n"
            f"Record B\n{pair['right_code']}  {pair['right_name']}\n{pair['right_village']}  {pair['right_mobile']}\n\n"
            f"{pair['reason']}",
        )

    def _keep(self):
        pair = self._selected()
        if pair is None:
            return
        DuplicateService.keep_both(pair["left_id"], pair["right_id"], self.user.id)
        self.reload()

    def _correct(self):
        self.open_module("Visitor Farmers", "")

    def _merge(self):
        pair = self._selected()
        if pair is None:
            return
        answer = QMessageBox.question(
            self,
            "Merge farmers",
            f"Keep {pair['left_code']} {pair['left_name']} and move every activity from "
            f"{pair['right_code']} {pair['right_name']} onto that record?\n\n"
            "The second farmer record will be removed. Farmer IDs already issued are not regenerated.",
        )
        if answer != QMessageBox.Yes:
            return
        try:
            DuplicateService.merge(pair["left_id"], pair["right_id"], self.user.id)
        except Exception as exc:
            QMessageBox.critical(self, "Merge", str(exc))
            return
        self.reload()


class ImportWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.rows = []
        self.review = {"valid": [], "invalid": [], "duplicates": []}
        layout = _page("Import farmers", "Choose a file, map the columns, and review the result. Invalid rows are never saved. You can cancel before import.")
        self.setLayout(layout)
        pick = QPushButton("Select Excel or CSV")
        pick.clicked.connect(self._pick)
        self.path_label = QLabel("No file selected.")
        self.path_label.setWordWrap(True)
        layout.addWidget(pick, 0, Qt.AlignLeft)
        layout.addWidget(self.path_label)
        self.preview = _table([])
        layout.addWidget(self.preview)
        self.map_form = QFormLayout()
        self.map_boxes = {}
        for field, label in ImportService.LABELS.items():
            box = QComboBox()
            self.map_boxes[field] = box
            self.map_form.addRow(label, box)
        layout.addLayout(self.map_form)
        actions = QHBoxLayout()
        check = QPushButton("Validate")
        check.setObjectName("SecondaryButton")
        check.clicked.connect(self._validate)
        self.confirm = QCheckBox("I have reviewed the valid rows and want to import them")
        save = QPushButton("Import valid rows")
        save.clicked.connect(self._commit)
        actions.addWidget(check)
        actions.addWidget(self.confirm)
        actions.addWidget(save)
        actions.addStretch(1)
        layout.addLayout(actions)
        self.result = QLabel("Validation has not been run.")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)
        self.result_table = _table(["Status", "Row", "Farmer", "Village", "Mobile", "Note"])
        layout.addWidget(self.result_table)

    def _pick(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select file", "", "Spreadsheets (*.xlsx *.csv)")
        if not path:
            return
        try:
            with busy(self, "Reading the file"):
                loaded = ImportService.read_file(path)
        except Exception as exc:
            QMessageBox.critical(self, "Import", f"Could not read the file.\n{exc}")
            return
        self.rows = loaded["rows"]
        columns = loaded["columns"]
        self.path_label.setText(f"{path}   ·   {len(self.rows)} rows")
        self.preview.setColumnCount(len(columns))
        self.preview.setHorizontalHeaderLabels(columns)
        _fill(self.preview, [[row.get(column, "") for column in columns] for row in self.rows[:8]])
        suggestion = ImportService.suggest_mapping(columns)
        for field, box in self.map_boxes.items():
            box.clear()
            box.addItem("(not mapped)", "")
            for column in columns:
                box.addItem(column, column)
            if suggestion.get(field):
                index = box.findData(suggestion[field])
                if index >= 0:
                    box.setCurrentIndex(index)
        self.review = {"valid": [], "invalid": [], "duplicates": []}
        self.confirm.setChecked(False)
        self.result.setText("File loaded. Map the columns, then validate.")

    def _mapping(self):
        return {field: box.currentData() or "" for field, box in self.map_boxes.items()}

    def _validate(self):
        if not self.rows:
            QMessageBox.information(self, "Import", "Select a file first.")
            return
        mapping = self._mapping()
        missing = [ImportService.LABELS[field] for field in ImportService.REQUIRED if not mapping.get(field)]
        if missing:
            QMessageBox.warning(self, "Import", "Map these columns first: " + ", ".join(missing))
            return
        with busy(self, "Checking the rows"):
            self.review = ImportService.review(self.rows, mapping)
        lines = []
        for status, key in (("Valid", "valid"), ("Invalid", "invalid"), ("Duplicate", "duplicates")):
            for row in self.review[key]:
                lines.append([status, row["row_number"], row["farmer_name"], row["village"], row["contact_number"], row.get("problems", "")])
        _fill(self.result_table, lines)
        self.result.setText(
            f"Valid records: {len(self.review['valid'])}    "
            f"Invalid records: {len(self.review['invalid'])}    "
            f"Duplicate candidates: {len(self.review['duplicates'])}"
        )
        SettingsService.put("last_import_invalid", str(len(self.review["invalid"])))

    def _commit(self):
        if not self.review["valid"]:
            QMessageBox.information(self, "Import", "Validate the file first. There are no valid rows to import.")
            return
        if not self.confirm.isChecked():
            QMessageBox.information(self, "Import", "Tick the confirmation box, or cancel and leave the data unchanged.")
            return
        answer = QMessageBox.question(
            self,
            "Confirm import",
            f"Import {len(self.review['valid'])} valid rows into PostgreSQL?\n\nInvalid and duplicate rows will be left out.",
        )
        if answer != QMessageBox.Yes:
            return
        try:
            with busy(self, "Importing records"):
                saved = ImportService.commit(self.review["valid"], self.user.id)
        except Exception as exc:
            QMessageBox.critical(self, "Import", str(exc))
            return
        self.rows = []
        self.review = {"valid": [], "invalid": [], "duplicates": []}
        self.confirm.setChecked(False)
        QMessageBox.information(self, "Import", f"Imported {saved} records. Each new farmer received a Farmer ID.")


class CalendarWidget(QWidget):
    def __init__(self, open_module):
        super().__init__()
        self.open_module = open_module
        self.events = []
        self._marked = []
        layout = _page("Activity calendar", "Training, OFT, FLD, extension, and vocational activities for the selected month.")
        self.setLayout(layout)
        body = QHBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.currentPageChanged.connect(self._load_month)
        self.calendar.selectionChanged.connect(self._show_day)
        body.addWidget(self.calendar, 1)
        side = QVBoxLayout()
        self.day_label = QLabel("Activities")
        self.day_label.setObjectName("CardTitle")
        self.table = _table(["Type", "Title", "Farmer ID"])
        self.table.cellDoubleClicked.connect(lambda _r, _c: self._open_selected())
        side.addWidget(self.day_label)
        side.addWidget(self.table)
        body.addLayout(side, 1)
        layout.addLayout(body)
        self._load_month(self.calendar.yearShown(), self.calendar.monthShown())

    def _load_month(self, year, month):
        blank = QTextCharFormat()
        for marked in self._marked:
            self.calendar.setDateTextFormat(marked, blank)
        self._marked = []
        self.events = InsightService.month_events(year, month)
        highlight = QTextCharFormat()
        highlight.setBackground(QColor("#d8f3df"))
        for event in self.events:
            marked = QDate(event["activity_date"].year, event["activity_date"].month, event["activity_date"].day)
            self.calendar.setDateTextFormat(marked, highlight)
            self._marked.append(marked)
        self._show_day()

    def _show_day(self):
        selected = self.calendar.selectedDate().toPyDate()
        day_events = [event for event in self.events if event["activity_date"] == selected]
        self.day_label.setText(f"Activities on {selected:%d-%m-%Y}")
        _fill(self.table, [[event["module"], event["title"], event["identifier"]] for event in day_events])
        self._day_events = day_events
        if not day_events:
            _fill(self.table, [["No activities", "Nothing is scheduled on this date.", ""]])

    def _open_selected(self):
        row = self.table.currentRow()
        if 0 <= row < len(getattr(self, "_day_events", [])):
            self.open_module(self._day_events[row]["open_module"], self._day_events[row].get("identifier") or "")


class VillageWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = _page("Village analysis", "Farmers and activities grouped by village.")
        self.setLayout(layout)
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter village")
        self.sort_box = QComboBox()
        self.sort_box.addItems(["Farmers", "Activities", "OFT", "FLD", "Training participation", "Village"])
        apply_btn = QPushButton("Apply")
        export_btn = QPushButton("Export CSV")
        export_btn.setObjectName("SecondaryButton")
        apply_btn.clicked.connect(self.reload)
        export_btn.clicked.connect(self._export)
        filters.addWidget(self.search)
        filters.addWidget(self.sort_box)
        filters.addWidget(apply_btn)
        filters.addWidget(export_btn)
        layout.addLayout(filters)
        self.chart = SimpleChart("Farmers by village")
        self.table = _table(["Village", "Total farmers", "Activities", "OFT", "FLD", "Training participation"])
        layout.addWidget(self.chart)
        layout.addWidget(self.table)
        self.shown = []
        self.reload()

    def reload(self):
        rows = InsightService.villages()
        text = self.search.text().strip().lower()
        if text:
            rows = [row for row in rows if text in row["village"].lower()]
        key = {
            "Farmers": "farmers",
            "Activities": "activities",
            "OFT": "oft",
            "FLD": "fld",
            "Training participation": "training_participation",
        }.get(self.sort_box.currentText())
        if key:
            rows = sorted(rows, key=lambda row: row[key], reverse=True)
        else:
            rows = sorted(rows, key=lambda row: row["village"].lower())
        self.shown = rows
        _fill(self.table, [[row["village"], row["farmers"], row["activities"], row["oft"], row["fld"], row["training_participation"]] for row in rows])
        self.chart.set_data([{"label": row["village"], "value": row["farmers"]} for row in rows[:8]])

    def _export(self):
        _export_rows(
            self,
            ["Village", "Total farmers", "Activities", "OFT", "FLD", "Training participation"],
            [[row["village"], row["farmers"], row["activities"], row["oft"], row["fld"], row["training_participation"]] for row in self.shown],
            "village_analysis.csv",
        )


class YearCompareWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = _page("Year comparison", "Financial year runs from April to March, for example 2025-26.")
        self.setLayout(layout)
        years = InsightService.financial_years()
        row = QHBoxLayout()
        self.left = QComboBox()
        self.right = QComboBox()
        self.left.addItems(years)
        self.right.addItems(years)
        if len(years) > 1:
            self.left.setCurrentIndex(max(0, len(years) - 2))
            self.right.setCurrentIndex(len(years) - 1)
        button = QPushButton("Compare")
        button.clicked.connect(self.reload)
        row.addWidget(QLabel("From"))
        row.addWidget(self.left)
        row.addWidget(QLabel("To"))
        row.addWidget(self.right)
        row.addWidget(button)
        row.addStretch(1)
        layout.addLayout(row)
        self.cards = QLabel("")
        self.cards.setWordWrap(True)
        self.chart = SimpleChart("Change")
        self.table = _table(["Item", "First year", "Second year", "Change"])
        layout.addWidget(self.cards)
        layout.addWidget(self.chart)
        layout.addWidget(self.table)
        self.reload()

    def reload(self):
        rows = InsightService.compare_years(self.left.currentText(), self.right.currentText())
        _fill(self.table, [[row["label"], row["left"], row["right"], row["change"]] for row in rows])
        self.cards.setText("   ".join(f"{row['label']}: {row['left']} → {row['right']}" for row in rows))
        self.chart.set_data([{"label": row["label"], "value": abs(row["change"])} for row in rows])


class AlertsWidget(QWidget):
    def __init__(self, open_module):
        super().__init__()
        self.open_module = open_module
        layout = _page("Smart alerts", "These alerts stay inside the application. Staff review them before changing any record.")
        self.setLayout(layout)
        refresh = QPushButton("Refresh")
        refresh.setObjectName("SecondaryButton")
        refresh.clicked.connect(self.reload)
        layout.addWidget(refresh, 0, Qt.AlignLeft)
        self.table = _table(["Alert", "Detail"])
        self.table.cellDoubleClicked.connect(lambda _r, _c: self._open())
        layout.addWidget(self.table)
        anomaly_title = QLabel("Anomalies")
        anomaly_title.setObjectName("CardTitle")
        note = QLabel("Unusual value detected. Please verify. These rows are statistical checks, not an automatic decision.")
        note.setWordWrap(True)
        self.anomalies = _table(["Module", "Record", "Date", "Message"])
        self.anomalies.cellDoubleClicked.connect(lambda _r, _c: self._open_anomaly())
        layout.addWidget(anomaly_title)
        layout.addWidget(note)
        layout.addWidget(self.anomalies)
        self.alert_rows = []
        self.anomaly_rows = []
        self.reload()

    def reload(self):
        self.alert_rows = InsightService.alerts()
        self.anomaly_rows = AnomalyService.find()
        _fill(self.table, [[row["title"], row["detail"]] for row in self.alert_rows] or [["No alerts", "Nothing needs attention right now."]])
        _fill(self.anomalies, [[row["module"], row["title"], row["activity_date"], row["message"]] for row in self.anomaly_rows])
        if not self.anomaly_rows:
            _fill(self.anomalies, [["—", "No unusual values", "", ""]])

    def _open(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.alert_rows):
            self.open_module(self.alert_rows[row]["open_module"], "")

    def _open_anomaly(self):
        row = self.anomalies.currentRow()
        if 0 <= row < len(self.anomaly_rows):
            self.open_module(self.anomaly_rows[row]["open_module"], self.anomaly_rows[row].get("identifier") or "")


class SettingsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        layout = _page("Settings", "KVK name and address appear on reports. Seasons stay Kharif and Rabi because activity records use those values.")
        self.setLayout(layout)
        form = QFormLayout()
        self.kvk_name = QLineEdit()
        self.kvk_address = QLineEdit()
        self.backup_folder = QLineEdit()
        self.timeout = QSpinBox()
        self.timeout.setRange(0, 240)
        self.timeout.setSuffix(" min")
        browse = QPushButton("Browse")
        browse.setObjectName("SecondaryButton")
        browse.clicked.connect(self._browse)
        folder_row = QHBoxLayout()
        folder_row.addWidget(self.backup_folder)
        folder_row.addWidget(browse)
        form.addRow("KVK name", self.kvk_name)
        form.addRow("KVK address", self.kvk_address)
        form.addRow("Backup folder", folder_row)
        form.addRow("Session timeout (0 keeps the session open)", self.timeout)
        layout.addLayout(form)
        save = QPushButton("Save settings")
        save.clicked.connect(self._save)
        layout.addWidget(save, 0, Qt.AlignLeft)
        dept_title = QLabel("Departments")
        dept_title.setObjectName("CardTitle")
        layout.addWidget(dept_title)
        self.departments = QLabel("")
        self.departments.setWordWrap(True)
        self.new_department = QLineEdit()
        self.new_department.setPlaceholderText("New department name")
        add = QPushButton("Add department")
        add.setObjectName("SecondaryButton")
        add.clicked.connect(self._add_department)
        dept_row = QHBoxLayout()
        dept_row.addWidget(self.new_department)
        dept_row.addWidget(add)
        layout.addWidget(self.departments)
        layout.addLayout(dept_row)
        password_title = QLabel("Change password")
        password_title.setObjectName("CardTitle")
        layout.addWidget(password_title)
        password_form = QFormLayout()
        self.current_password = QLineEdit()
        self.new_password = QLineEdit()
        self.confirm_password = QLineEdit()
        for box in (self.current_password, self.new_password, self.confirm_password):
            box.setEchoMode(QLineEdit.Password)
        password_form.addRow("Current password", self.current_password)
        password_form.addRow("New password", self.new_password)
        password_form.addRow("Confirm new password", self.confirm_password)
        layout.addLayout(password_form)
        change = QPushButton("Change password")
        change.setObjectName("SecondaryButton")
        change.clicked.connect(self._change_password)
        layout.addWidget(change, 0, Qt.AlignLeft)
        layout.addStretch(1)
        self._load()

    def _load(self):
        values = SettingsService.all_values()
        self.kvk_name.setText(values.get("kvk_name", ""))
        self.kvk_address.setText(values.get("kvk_address", ""))
        self.backup_folder.setText(values.get("backup_folder", "backups"))
        self.timeout.setValue(int(values.get("session_timeout_minutes") or "30"))
        names = ", ".join(row.name for row in ActivityService.list_departments())
        self.departments.setText(names)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Backup folder", self.backup_folder.text() or "backups")
        if folder:
            self.backup_folder.setText(folder)

    def _save(self):
        if not self.kvk_name.text().strip():
            QMessageBox.warning(self, "Settings", "Enter the KVK name.")
            return
        answer = QMessageBox.question(self, "Save settings", "Save these application settings?")
        if answer != QMessageBox.Yes:
            return
        SettingsService.save(
            {
                "kvk_name": self.kvk_name.text().strip(),
                "kvk_address": self.kvk_address.text().strip(),
                "backup_folder": self.backup_folder.text().strip() or "backups",
                "session_timeout_minutes": str(self.timeout.value()),
            },
            self.user.id,
        )
        window = self.window()
        if hasattr(window, "apply_session_timeout"):
            window.apply_session_timeout()
        QMessageBox.information(self, "Settings", "Settings saved.")

    def _add_department(self):
        answer = QMessageBox.question(self, "Add department", f"Add department '{self.new_department.text().strip()}'?")
        if answer != QMessageBox.Yes:
            return
        try:
            SettingsService.add_department(self.new_department.text(), self.user.id)
        except Exception as exc:
            QMessageBox.warning(self, "Settings", str(exc))
            return
        self.new_department.clear()
        self._load()

    def _change_password(self):
        if self.new_password.text() != self.confirm_password.text():
            QMessageBox.warning(self, "Password", "The new password and confirmation do not match.")
            return
        answer = QMessageBox.question(self, "Change password", "Change the password for this account?")
        if answer != QMessageBox.Yes:
            return
        try:
            AuthController.change_password(self.user.id, self.current_password.text(), self.new_password.text())
        except Exception as exc:
            QMessageBox.warning(self, "Password", str(exc))
            return
        self.current_password.clear()
        self.new_password.clear()
        self.confirm_password.clear()
        QMessageBox.information(self, "Password", "Password changed.")


def _stamp(value):
    if not value:
        return ""
    return value.strftime("%d-%m-%Y %H:%M")


class ScrollPage(QScrollArea):
    def __init__(self, widget):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setWidget(widget)
