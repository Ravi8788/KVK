from datetime import datetime
from math import ceil

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.activity_service import ActivityService
from services.report_service import ReportService


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
        filter_layout = QHBoxLayout(filter_card)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        self.department_combo = QComboBox()
        self.department_combo.addItem("All", None)
        for dept in self.departments:
            self.department_combo.addItem(dept.name, dept.id)

        self.module_combo = QComboBox()
        self.module_combo.addItems(["All"] + ActivityService.MODULES)

        apply_btn = QPushButton("Apply Filters")
        apply_btn.clicked.connect(self._apply_filters)

        export_pdf_btn = QPushButton("Export PDF")
        export_csv_btn = QPushButton("Export CSV")
        export_pdf_btn.clicked.connect(self._export_pdf)
        export_csv_btn.clicked.connect(self._export_csv)

        filter_layout.addWidget(QLabel("From"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("To"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(QLabel("Department"))
        filter_layout.addWidget(self.department_combo)
        filter_layout.addWidget(QLabel("Module"))
        filter_layout.addWidget(self.module_combo)
        filter_layout.addWidget(apply_btn)
        filter_layout.addWidget(export_pdf_btn)
        filter_layout.addWidget(export_csv_btn)

        root.addWidget(filter_card)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)

        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "Module",
                "Farmer",
                "Village",
                "District",
                "Tehsil",
                "Contact",
                "Date",
                "Department",
                "Season",
                "Activity",
            ]
        )
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        table_layout.addWidget(self.table)

        pager = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
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
        return {
            "start_date": self.start_date.date().toPyDate(),
            "end_date": self.end_date.date().toPyDate(),
            "department_id": self.department_combo.currentData(),
            "module_type": self.module_combo.currentText(),
        }

    def _apply_filters(self) -> None:
        filters = self._active_filters()
        self.current_records, self.total_records = ReportService.query_records(
            start_date=filters["start_date"],
            end_date=filters["end_date"],
            department_id=filters["department_id"],
            module_type=filters["module_type"],
            page=self.current_page,
            page_size=self.page_size,
        )
        self._refresh_table()

    def _refresh_table(self) -> None:
        self.table.setRowCount(0)
        for row_idx, row in enumerate(self.current_records):
            self.table.insertRow(row_idx)
            values = [
                row["id"],
                row["module_type"],
                row["farmer_name"],
                row["village"],
                row["district"],
                row["tehsil"],
                row["contact_number"],
                str(row["activity_date"]),
                row["department"],
                row["season"],
                row["activity_type"],
            ]
            for col, value in enumerate(values):
                self.table.setItem(row_idx, col, QTableWidgetItem(str(value)))

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
            output = ReportService.export_pdf(self.current_records, path, "KVK Activity Report")
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
            output = ReportService.export_csv(self.current_records, path)
            ReportService.record_report_generation(self.current_user.id, "KVK CSV Report", self._active_filters(), output)
            QMessageBox.information(self, "Exported", f"CSV saved to: {output}")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"CSV export failed: {exc}")

    def _prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self._apply_filters()

    def _next_page(self) -> None:
        total_pages = max(1, ceil(self.total_records / self.page_size))
        if self.current_page < total_pages:
            self.current_page += 1
            self._apply_filters()
