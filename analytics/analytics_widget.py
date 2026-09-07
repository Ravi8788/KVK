import csv
import os
from datetime import datetime

from PyQt5.QtCore import QDate, Qt, QRectF, QPointF
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush
from PyQt5.QtWidgets import (
    QComboBox, QDateEdit, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph

from analytics.analytics_service import AnalyticsService
from services.report_service import ReportService


class SimpleChart(QWidget):
    """Small dependency-free bar/line chart rendered with QPainter."""

    def __init__(self, title, chart_type="bar", parent=None):
        super().__init__(parent)
        self.title = title
        self.chart_type = chart_type
        self.items = []
        self.setMinimumHeight(245)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_data(self, items):
        self.items = items or []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#ffffff"))
        painter.setPen(QColor("#225d36"))
        painter.drawText(16, 24, self.title)
        if not self.items:
            painter.setPen(QColor("#6c7b6c"))
            painter.drawText(16, 58, "No data available for the selected filters.")
            return
        data = self.items[-24:]
        left, top, right, bottom = 48, 48, 18, 42
        plot = QRectF(left, top, max(1, self.width() - left - right), max(1, self.height() - top - bottom))
        maximum = max(float(item.get("value", 0)) for item in data) or 1
        painter.setPen(QPen(QColor("#dcebdc"), 1))
        painter.drawLine(QPointF(plot.left(), plot.bottom()), QPointF(plot.right(), plot.bottom()))
        painter.setPen(QColor("#6c7b6c"))
        painter.drawText(8, int(plot.top() + 5), str(int(maximum)))
        painter.drawText(18, int(plot.bottom() + 20), "0")
        if self.chart_type == "line":
            points = []
            for index, item in enumerate(data):
                x = plot.left() + (plot.width() * index / max(1, len(data) - 1))
                y = plot.bottom() - (plot.height() * float(item.get("value", 0)) / maximum)
                points.append(QPointF(x, y))
            painter.setPen(QPen(QColor("#2e8b57"), 3))
            for first, second in zip(points, points[1:]):
                painter.drawLine(first, second)
            painter.setBrush(QBrush(QColor("#2e8b57")))
            for point in points:
                painter.drawEllipse(point, 4, 4)
        else:
            width = plot.width() / max(1, len(data))
            painter.setBrush(QBrush(QColor("#5aa469")))
            painter.setPen(Qt.NoPen)
            for index, item in enumerate(data):
                value = float(item.get("value", 0))
                height = plot.height() * value / maximum
                bar = QRectF(plot.left() + index * width + width * 0.16, plot.bottom() - height, width * 0.68, height)
                painter.drawRect(bar)
        painter.setPen(QColor("#385238"))
        for index, item in enumerate(data):
            label = str(item.get("label", ""))[:14]
            x = plot.left() + (plot.width() * index / max(1, len(data) - 1)) if self.chart_type == "line" else plot.left() + index * (plot.width() / len(data)) + (plot.width() / len(data)) / 2
            painter.save()
            painter.translate(x, plot.bottom() + 30)
            painter.rotate(-35 if len(data) > 6 else 0)
            painter.drawText(0, 0, label)
            painter.restore()


class AnalyticsWidget(QWidget):
    """Analytics dashboard and dynamic pivot analysis page."""

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.departments = []
        self.dashboard_data = {}
        self._build_ui()
        self._load_options()
        self._apply_filters()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 10)
        root.setSpacing(8)
        title_row = QHBoxLayout()
        title = QLabel("Analytics & Pivot Analysis")
        title.setObjectName("CardTitle")
        title_row.addWidget(title)
        title_row.addStretch(1)
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("AnalyticsStatus")
        title_row.addWidget(self.status_label)
        root.addLayout(title_row)

        self.tabs = QTabWidget()
        self.dashboard_tab = self._build_dashboard_tab()
        self.pivot_tab = self._build_pivot_tab()
        self.tabs.addTab(self.dashboard_tab, "Analytics Dashboard")
        self.tabs.addTab(self.pivot_tab, "Pivot Analysis")
        root.addWidget(self.tabs)

    def _build_filter_row(self):
        card = QFrame()
        card.setObjectName("Card")
        layout = QGridLayout(card)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(4)
        self.from_date = QDateEdit(QDate.currentDate().addYears(-1))
        self.from_date.setCalendarPopup(True)
        self.to_date = QDateEdit(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        self.department = QComboBox()
        self.module = QComboBox()
        self.season = QComboBox()
        self.district = QComboBox()
        self.tehsil = QComboBox()
        self.village = QComboBox()
        self.category = QComboBox()
        self.activity_type = QComboBox()
        for widget in [self.department, self.module, self.activity_type, self.season, self.district, self.tehsil, self.village, self.category]:
            widget.setMinimumWidth(145)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.from_date.setMinimumWidth(125)
        self.to_date.setMinimumWidth(125)
        fields = [("From", self.from_date), ("To", self.to_date), ("Department", self.department), ("Module", self.module), ("Activity Type", self.activity_type), ("Season", self.season), ("District", self.district), ("Taluka / Tehsil", self.tehsil), ("Village", self.village), ("Farmer Category", self.category)]
        for index, (label, widget) in enumerate(fields):
            row, column = divmod(index, 5)
            layout.addWidget(QLabel(label), row * 2, column)
            layout.addWidget(widget, row * 2 + 1, column)
        for column in range(5):
            layout.setColumnStretch(column, 1)
        self.apply_button = QPushButton("Apply Filters")
        self.reset_button = QPushButton("Reset Filters")
        self.apply_button.clicked.connect(self._apply_filters)
        self.reset_button.clicked.connect(self._reset_filters)
        layout.addWidget(self.apply_button, 4, 3)
        layout.addWidget(self.reset_button, 4, 4)
        return card

    def _build_dashboard_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(self._build_filter_row())
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.dashboard_layout = QVBoxLayout(content)
        self.dashboard_layout.setContentsMargins(4, 4, 4, 4)
        self.dashboard_layout.setSpacing(10)
        self.kpi_grid = QGridLayout()
        self.kpi_grid.setHorizontalSpacing(10)
        self.kpi_grid.setVerticalSpacing(10)
        self.dashboard_layout.addLayout(self.kpi_grid)
        charts = QGridLayout()
        charts.setHorizontalSpacing(10)
        charts.setVerticalSpacing(10)
        self.department_chart = SimpleChart("Activities by Department")
        self.trend_chart = SimpleChart("Activities Over Time", "line")
        self.module_chart = SimpleChart("Farmer Participation by Activity Type")
        self.season_chart = SimpleChart("Season-wise Participation")
        self.category_chart = SimpleChart("Farmer Category Analysis")
        self.village_chart = SimpleChart("Top Villages")
        for index, chart in enumerate([self.department_chart, self.trend_chart, self.module_chart, self.season_chart, self.category_chart, self.village_chart]):
            charts.addWidget(self._chart_card(chart), index // 2, index % 2)
        self.dashboard_layout.addLayout(charts)
        self.performance_table = QTableWidget(0, 6)
        self.performance_table.setHorizontalHeaderLabels(["Department", "Activities", "Participants", "Trainings", "OFT", "FLD"])
        self.performance_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.performance_table.setMinimumHeight(150)
        self.performance_table.setMaximumHeight(245)
        self.performance_table.horizontalHeader().setStretchLastSection(True)
        self.dashboard_layout.addWidget(QLabel("Department Performance"))
        self.dashboard_layout.addWidget(self.performance_table)
        export_row = QHBoxLayout()
        export_csv = QPushButton("Export Analytics CSV")
        export_pdf = QPushButton("Export Analytics PDF")
        export_csv.clicked.connect(self._export_csv)
        export_pdf.clicked.connect(self._export_pdf)
        export_row.addWidget(export_csv)
        export_row.addWidget(export_pdf)
        export_row.addStretch(1)
        self.dashboard_layout.addLayout(export_row)
        self.dashboard_layout.addStretch(1)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        return page

    def _chart_card(self, chart):
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumHeight(275)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(chart)
        return card

    def _build_pivot_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        card = QFrame()
        card.setObjectName("Card")
        controls = QGridLayout(card)
        controls.setContentsMargins(12, 10, 12, 12)
        controls.setHorizontalSpacing(10)
        controls.setVerticalSpacing(6)
        self.pivot_row = QComboBox(); self.pivot_row.addItems(list(AnalyticsService.ROW_FIELDS))
        self.pivot_column = QComboBox(); self.pivot_column.addItems(list(AnalyticsService.ROW_FIELDS))
        self.pivot_value = QComboBox(); self.pivot_value.addItems(list(AnalyticsService.VALUE_FIELDS))
        self.pivot_aggregation = QComboBox(); self.pivot_aggregation.addItems(["Count", "Sum", "Average", "Minimum", "Maximum"])
        for widget in [self.pivot_row, self.pivot_column, self.pivot_value, self.pivot_aggregation]:
            widget.setMinimumWidth(170)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        controls.addWidget(QLabel("Rows"), 0, 0); controls.addWidget(self.pivot_row, 0, 1)
        controls.addWidget(QLabel("Columns"), 0, 2); controls.addWidget(self.pivot_column, 0, 3)
        controls.addWidget(QLabel("Values"), 1, 0); controls.addWidget(self.pivot_value, 1, 1)
        controls.addWidget(QLabel("Aggregation"), 1, 2); controls.addWidget(self.pivot_aggregation, 1, 3)
        generate = QPushButton("Generate Pivot"); reset = QPushButton("Reset"); csv_button = QPushButton("Export CSV"); pdf_button = QPushButton("Export PDF")
        generate.clicked.connect(self._generate_pivot); reset.clicked.connect(self._reset_pivot); csv_button.clicked.connect(self._export_pivot_csv); pdf_button.clicked.connect(self._export_pivot_pdf)
        controls.addWidget(generate, 2, 0); controls.addWidget(reset, 2, 1); controls.addWidget(csv_button, 2, 2); controls.addWidget(pdf_button, 2, 3)
        layout.addWidget(card)
        self.pivot_table = QTableWidget(0, 0)
        self.pivot_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pivot_table.setAlternatingRowColors(True)
        self.pivot_table.horizontalHeader().setStretchLastSection(True)
        self.pivot_table.cellDoubleClicked.connect(self._show_drilldown)
        layout.addWidget(self.pivot_table)
        self.pivot_status = QLabel("Generate a pivot from the current dashboard filters.")
        layout.addWidget(self.pivot_status)
        return page

    def _load_options(self):
        from services.activity_service import ActivityService
        self.departments = ActivityService.list_departments()
        options = AnalyticsService.filter_options()
        self._fill(self.department, [(d.name, d.id) for d in self.departments], True)
        self._fill(self.module, [(name, name) for name in AnalyticsService.MODULES], True)
        for combo, key in [(self.season, "seasons"), (self.district, "districts"), (self.tehsil, "tehsils"), (self.village, "villages"), (self.category, "categories")]:
            self._fill(combo, [(value, value) for value in options[key]], True)
        self.activity_types = options["activity_types"]
        self._fill(self.activity_type, [(name, name) for name in self.activity_types], True)

    @staticmethod
    def _fill(combo, values, include_all):
        combo.clear()
        if include_all:
            combo.addItem("All", None)
        for label, value in values:
            combo.addItem(label, value)

    def _filters(self):
        return {"start_date": self.from_date.date().toPyDate(), "end_date": self.to_date.date().toPyDate(), "department_id": self.department.currentData(), "module_type": self.module.currentData(), "activity_type": self.activity_type.currentData(), "season": self.season.currentData(), "district": self.district.currentData(), "tehsil": self.tehsil.currentData(), "village": self.village.currentData(), "farmer_category": self.category.currentData()}

    def _apply_filters(self):
        try:
            self.dashboard_data = AnalyticsService.dashboard(self._filters())
            self._refresh_dashboard()
            self.status_label.setText("Updated")
        except Exception as exc:
            self.status_label.setText("Database error")
            QMessageBox.critical(self, "Analytics Error", f"Could not load analytics: {exc}")

    def _refresh_dashboard(self):
        for index in reversed(range(self.kpi_grid.count())):
            item = self.kpi_grid.takeAt(index)
            if item.widget(): item.widget().deleteLater()
        for index, (label, value) in enumerate(self.dashboard_data.get("kpis", {}).items()):
            card = QFrame(); card.setObjectName("Card")
            card_layout = QVBoxLayout(card)
            name = QLabel(label); number = QLabel(f"{value:,}"); number.setObjectName("AnalyticsValue")
            card_layout.addWidget(name); card_layout.addWidget(number)
            self.kpi_grid.addWidget(card, index // 4, index % 4)
        self.department_chart.set_data(self.dashboard_data.get("by_department"))
        self.trend_chart.set_data(self.dashboard_data.get("by_time"))
        self.module_chart.set_data(self.dashboard_data.get("by_module"))
        self.season_chart.set_data(self.dashboard_data.get("by_season"))
        self.category_chart.set_data(self.dashboard_data.get("by_category"))
        self.village_chart.set_data(self.dashboard_data.get("top_villages"))
        rows = self.dashboard_data.get("department_performance", [])
        self.performance_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [row["department"], row["activities"], row["participants"], row["trainings"], row["oft"], row["fld"]]
            for c, value in enumerate(values): self.performance_table.setItem(r, c, QTableWidgetItem(str(value)))

    def _reset_filters(self):
        self.from_date.setDate(QDate.currentDate().addYears(-1)); self.to_date.setDate(QDate.currentDate())
        for combo in [self.department, self.module, self.activity_type, self.season, self.district, self.tehsil, self.village, self.category]: combo.setCurrentIndex(0)
        self._apply_filters()

    def _generate_pivot(self):
        try:
            result = AnalyticsService.pivot(self._filters(), self.pivot_row.currentText(), self.pivot_column.currentText(), self.pivot_value.currentText(), self.pivot_aggregation.currentText())
            columns = result["columns"]
            self.pivot_table.setColumnCount(len(columns) + 1); self.pivot_table.setHorizontalHeaderLabels([self.pivot_row.currentText()] + columns)
            self.pivot_table.setRowCount(len(result["rows"]))
            for r, row in enumerate(result["rows"]):
                self.pivot_table.setItem(r, 0, QTableWidgetItem(row))
                for c, column in enumerate(columns, 1): self.pivot_table.setItem(r, c, QTableWidgetItem(str(result["matrix"][row][column])))
            self.pivot_table.resizeColumnsToContents(); self.pivot_status.setText(f"{len(result['rows'])} rows, {len(columns)} columns. Double-click a row to drill down.")
            self.pivot_result = result
        except Exception as exc:
            QMessageBox.critical(self, "Pivot Error", f"Could not generate pivot: {exc}")

    def _reset_pivot(self):
        self.pivot_table.clear(); self.pivot_table.setRowCount(0); self.pivot_table.setColumnCount(0); self.pivot_status.setText("Pivot reset.")

    def _show_drilldown(self, row, column):
        if row < 0 or not hasattr(self, "pivot_result"): return
        label = self.pivot_table.item(row, 0).text()
        filters = self._filters(); field = AnalyticsService.ROW_FIELDS[self.pivot_row.currentText()]
        filters[field] = label
        records = AnalyticsService.detail_records(filters)
        dialog = QTableWidget(len(records), 7, self)
        dialog.setWindowTitle(f"Drill-down: {label}"); dialog.setHorizontalHeaderLabels(["ID", "Date", "Module", "Activity", "Department", "Farmer", "Village"])
        for r, record in enumerate(records):
            for c, key in enumerate(["id", "date", "module", "activity", "department", "farmer", "village"]): dialog.setItem(r, c, QTableWidgetItem(str(record[key])))
        dialog.resize(900, 400); dialog.show(); self._drilldown_dialog = dialog

    def _export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Analytics CSV", f"kvk_analytics_{datetime.now():%Y%m%d_%H%M%S}.csv", "CSV Files (*.csv)")
        if not path: return
        rows = self.dashboard_data.get("department_performance", [])
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["department", "activities", "participants", "trainings", "oft", "fld"]); writer.writeheader(); writer.writerows(rows)
            ReportService.record_report_generation(self.current_user.id, "KVK Analytics CSV", self._filters(), path)
            QMessageBox.information(self, "Exported", f"Analytics CSV saved to: {path}")
        except Exception as exc: QMessageBox.critical(self, "Export Error", str(exc))

    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Analytics PDF", f"kvk_analytics_{datetime.now():%Y%m%d_%H%M%S}.pdf", "PDF Files (*.pdf)")
        if not path: return
        try:
            rows = self.dashboard_data.get("department_performance", [])
            data = [["Department", "Activities", "Participants", "Trainings", "OFT", "FLD"]] + [[r["department"], r["activities"], r["participants"], r["trainings"], r["oft"], r["fld"]] for r in rows]
            doc = SimpleDocTemplate(path, pagesize=landscape(A4)); styles = getSampleStyleSheet(); story = [Paragraph("KVK Analytics Report", styles["Title"]), Spacer(1, 12), Paragraph(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}", styles["Normal"]), Spacer(1, 12), Table(data, repeatRows=1)]
            story[-1].setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E8B57")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])]))
            doc.build(story); ReportService.record_report_generation(self.current_user.id, "KVK Analytics PDF", self._filters(), path); QMessageBox.information(self, "Exported", f"Analytics PDF saved to: {path}")
        except Exception as exc: QMessageBox.critical(self, "Export Error", str(exc))

    def _export_pivot_csv(self):
        if not hasattr(self, "pivot_result"): QMessageBox.warning(self, "No Pivot", "Generate a pivot before exporting."); return
        path, _ = QFileDialog.getSaveFileName(self, "Save Pivot CSV", "kvk_pivot.csv", "CSV Files (*.csv)")
        if not path: return
        result = self.pivot_result
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle); writer.writerow([self.pivot_row.currentText()] + result["columns"])
            for row in result["rows"]: writer.writerow([row] + [result["matrix"][row][column] for column in result["columns"]])
        ReportService.record_report_generation(self.current_user.id, "KVK Pivot CSV", self._filters(), path)
        QMessageBox.information(self, "Exported", f"Pivot CSV saved to: {path}")

    def _export_pivot_pdf(self):
        if not hasattr(self, "pivot_result"): QMessageBox.warning(self, "No Pivot", "Generate a pivot before exporting."); return
        path, _ = QFileDialog.getSaveFileName(self, "Save Pivot PDF", "kvk_pivot.pdf", "PDF Files (*.pdf)")
        if not path: return
        result = self.pivot_result; data = [[self.pivot_row.currentText()] + result["columns"]]
        data.extend([[row] + [result["matrix"][row][column] for column in result["columns"]] for row in result["rows"]])
        doc = SimpleDocTemplate(path, pagesize=landscape(A4)); table = Table(data, repeatRows=1); table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E8B57")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)])); doc.build([Paragraph("KVK Pivot Analysis", getSampleStyleSheet()["Title"]), Spacer(1, 12), table]); QMessageBox.information(self, "Exported", f"Pivot PDF saved to: {path}")
        ReportService.record_report_generation(self.current_user.id, "KVK Pivot PDF", self._filters(), path)
