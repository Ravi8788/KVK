from datetime import datetime
from math import ceil

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.activity_service import ActivityService
from services.report_service import ReportService
from ui.loading_overlay import busy


class ReportsWidget(QWidget):
    """Report table with filters, pagination, and PDF/CSV export."""

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.departments = ActivityService.list_departments()
        self.current_records = []
        self.current_page = 1
        self.page_size = 200
        self.total_records = 0
        self._build_ui()
        self._apply_filters()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Reports")
        title.setObjectName("CardTitle")
        root.addWidget(title)

        filter_card = QFrame()
        filter_card.setObjectName("Card")
        filter_layout = QGridLayout(filter_card)
        filter_layout.setContentsMargins(16, 14, 16, 14)
        filter_layout.setHorizontalSpacing(12)
        filter_layout.setVerticalSpacing(6)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd-MM-yyyy")
        self.start_date.setDate(QDate.currentDate().addYears(-1))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd-MM-yyyy")
        self.end_date.setDate(QDate.currentDate())

        self.department_combo = QComboBox()
        self.department_combo.addItem("All", None)
        for dept in self.departments:
            self.department_combo.addItem(dept.name, dept.id)

        self.module_combo = QComboBox()
        self.module_combo.addItems(["All"] + ActivityService.MODULES)

        self.season_combo = QComboBox()
        self.season_combo.addItems(["All", "Kharif", "Rabi"])
        self.village_input = QLineEdit()
        self.village_input.setPlaceholderText("Village")
        self.farmer_input = QLineEdit()
        self.farmer_input.setPlaceholderText("Name, ID, or mobile")
        self.activity_input = QLineEdit()
        self.activity_input.setPlaceholderText("Activity type")

        apply_btn = QPushButton("Apply filters")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.clicked.connect(self._apply_from_button)

        export_pdf_btn = QPushButton("Export PDF")
        export_csv_btn = QPushButton("Export CSV")
        export_pdf_btn.setObjectName("SecondaryButton")
        export_csv_btn.setObjectName("SecondaryButton")
        export_pdf_btn.setCursor(Qt.PointingHandCursor)
        export_csv_btn.setCursor(Qt.PointingHandCursor)
        export_pdf_btn.clicked.connect(self._export_pdf)
        export_csv_btn.clicked.connect(self._export_csv)
        print_btn = QPushButton("Print")
        print_btn.setObjectName("SecondaryButton")
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.clicked.connect(self._print_report)

        for column, (label, widget) in enumerate(
            (
                ("From", self.start_date),
                ("To", self.end_date),
                ("Department", self.department_combo),
                ("Module", self.module_combo),
            )
        ):
            filter_layout.addWidget(QLabel(label), 0, column)
            filter_layout.addWidget(widget, 1, column)

        actions = QHBoxLayout()
        actions.addWidget(apply_btn)
        actions.addWidget(export_pdf_btn)
        actions.addWidget(export_csv_btn)
        actions.addWidget(print_btn)
        actions.addStretch(1)

        for column, (label, widget) in enumerate(
            (
                ("Season", self.season_combo),
                ("Village", self.village_input),
                ("Farmer", self.farmer_input),
                ("Activity type", self.activity_input),
            )
        ):
            filter_layout.addWidget(QLabel(label), 2, column)
            filter_layout.addWidget(widget, 3, column)
        filter_layout.addLayout(actions, 4, 0, 1, 4)

        root.addWidget(filter_card)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)

        self.table = QTableWidget(0, 0)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)
        table_layout.addWidget(self.table)

        pager = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.prev_btn.setObjectName("SecondaryButton")
        self.next_btn.setObjectName("SecondaryButton")
        self.page_label = QLabel("Page 1")
        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn.clicked.connect(self._next_page)
        pager.addWidget(self.prev_btn)
        pager.addWidget(self.next_btn)
        pager.addWidget(self.page_label)
        pager.addStretch(1)
        table_layout.addLayout(pager)

        root.addWidget(table_card)

    def _active_filters(self) -> dict:
        department_name = self.department_combo.currentText().strip()
        return {
            "start_date": self.start_date.date().toPyDate(),
            "end_date": self.end_date.date().toPyDate(),
            "department_id": self.department_combo.currentData(),
            "department_name": "" if department_name == "All" else department_name,
            "module_type": self.module_combo.currentText(),
            "season": self.season_combo.currentText(),
            "village": self.village_input.text().strip(),
            "farmer_query": self.farmer_input.text().strip(),
            "activity_type": self.activity_input.text().strip(),
        }

    def _report_title(self) -> str:
        filters = self._active_filters()
        title = "KVK Activity Report"
        department_name = filters.get("department_name") or ""
        module_type = filters.get("module_type") or "All"
        if department_name:
            title = f"{title} - {department_name}"
        if module_type and module_type != "All":
            title = f"{title} - {module_type}"
        return title

    def _apply_from_button(self) -> None:
        self.current_page = 1
        self._apply_filters()

    def _apply_filters(self) -> None:
        filters = self._active_filters()
        with busy(self, "Loading report"):
            self.current_records, self.total_records = ReportService.query_records(
                start_date=filters["start_date"],
                end_date=filters["end_date"],
                department_id=filters["department_id"],
                module_type=filters["module_type"],
                season=filters["season"],
                village=filters["village"],
                farmer_query=filters["farmer_query"],
                activity_type=filters["activity_type"],
                page=self.current_page,
                page_size=self.page_size,
            )
            self._refresh_table()

    def _refresh_table(self) -> None:
        filters = self._active_filters()
        columns = ReportService.get_visible_columns(self.current_records, filters)
        labels = ReportService.get_header_labels(filters)
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([labels.get(column, column) for column in columns])
        self.table.setRowCount(0)
        for row_idx, row in enumerate(self.current_records):
            self.table.insertRow(row_idx)
            for col, column in enumerate(columns):
                self.table.setItem(row_idx, col, QTableWidgetItem(str(row.get(column, ""))))

        total_pages = max(1, ceil(self.total_records / self.page_size))
        self.page_label.setText(f"Page {self.current_page} of {total_pages} | Total records: {self.total_records}")

    def _export_pdf(self) -> None:
        if not self.current_records:
            QMessageBox.warning(self, "No Data", "Apply filters with available data before export.")
            return

        default_name = f"kvk_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", default_name, "PDF Files (*.pdf)")
        if not path:
            return

        try:
            output = ReportService.export_pdf(self.current_records, path, self._report_title(), self._active_filters())
            ReportService.record_report_generation(self.current_user.id, "KVK Activity Report", self._active_filters(), output)
            QMessageBox.information(self, "Exported", f"PDF saved to: {output}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"PDF export failed: {exc}")

    def _export_csv(self) -> None:
        if not self.current_records:
            QMessageBox.warning(self, "No Data", "Apply filters with available data before export.")
            return

        default_name = f"kvk_report_{datetime.now():%Y%m%d_%H%M%S}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", default_name, "CSV Files (*.csv)")
        if not path:
            return

        try:
            output = ReportService.export_csv(self.current_records, path, self._active_filters())
            ReportService.record_report_generation(self.current_user.id, "KVK CSV Report", self._active_filters(), output)
            QMessageBox.information(self, "Exported", f"CSV saved to: {output}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"CSV export failed: {exc}")

    def _print_report(self) -> None:
        if not self.current_records:
            QMessageBox.warning(self, "No Data", "Apply filters with available data before printing.")
            return
        from PyQt5.QtGui import QTextDocument
        from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
        from services.smart_service import SettingsService

        filters = self._active_filters()
        columns = ReportService.get_visible_columns(self.current_records, filters)
        labels = ReportService.get_header_labels(filters)
        header = "".join(f"<th>{labels.get(column, column)}</th>" for column in columns)
        body = []
        for row in self.current_records:
            cells = "".join(f"<td>{row.get(column, '')}</td>" for column in columns)
            body.append(f"<tr>{cells}</tr>")
        html = (
            f"<h2>{SettingsService.get('kvk_name')}</h2>"
            f"<h3>{self._report_title()}</h3>"
            f"<p>{filters['start_date']} to {filters['end_date']}</p>"
            f"<table border='1' cellspacing='0' cellpadding='3'><tr>{header}</tr>{''.join(body)}</table>"
        )
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() != dialog.Accepted:
            return
        document = QTextDocument()
        document.setHtml(html)
        document.print_(printer)
        ReportService.record_report_generation(self.current_user.id, "KVK Printed Report", filters, "print")

    def _prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self._apply_filters()

    def _next_page(self) -> None:
        total_pages = max(1, ceil(self.total_records / self.page_size))
        if self.current_page < total_pages:
            self.current_page += 1
            self._apply_filters()
