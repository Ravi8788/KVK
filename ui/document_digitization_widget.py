import os
import re
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


CATEGORIES = [
    "Visitor Farmers",
    "On Farm Testing (OFT)",
    "Front Line Demonstrations (FLD)",
    "Training Programmes",
    "Vocational Training Programmes",
    "Extension Activities",
    "Other Extension Activities",
]


# Field labels, database fields and types mirror the existing ActivityFormWidget
# and Activity/Farmer SQLAlchemy models. These definitions are UI-only; this page
# does not create or update database records.
FIELD_REGISTRY = {
    "Visitor Farmers": [
        ("Date*", "activity_date", "Date", True),
        ("Name of Farmer*", "farmer_name", "Text", True),
        ("District*", "visitor_district", "Text", True),
        ("Tehsil*", "visitor_tehsil", "Text", True),
        ("Village*", "village", "Text", True),
        ("Mobile No.*", "contact_number", "Mobile", True),
        ("Name of Scientist*", "visitor_scientist", "Text", True),
        ("Name of Dept.*", "department_id", "Reference", True),
        ("Purpose*", "activity_type", "Text", True),
    ],
    "On Farm Testing (OFT)": [
        ("Department*", "department_id", "Reference", True),
        ("Activity Type*", "activity_type", "Text", True),
        ("Season*", "season", "Choice", True),
        ("Date*", "activity_date", "Date", True),
        ("Title of OFT*", "oft_title", "Text", True),
        ("Crop Variety*", "oft_crop_variety", "Text", True),
        ("No. of Farmers*", "oft_farmer_count", "Integer", True),
        ("Technical Assessment*", "oft_technical_assessment", "Text", True),
        ("Area*", "oft_area", "Text", True),
        ("Farmer Name*", "farmer_name", "Text", True),
        ("Mobile No.*", "contact_number", "Mobile", True),
        ("Scientist*", "oft_farmer_scientist", "Text", True),
        ("Purpose*", "oft_farmer_purpose", "Text", True),
        ("District*", "oft_farmer_district", "Text", True),
        ("Tehsil*", "oft_farmer_tehsil", "Text", True),
        ("Category*", "oft_farmer_category", "Choice", True),
    ],
    "Front Line Demonstrations (FLD)": [
        ("Department*", "department_id", "Reference", True),
        ("Activity Type*", "activity_type", "Text", True),
        ("Season*", "season", "Choice", True),
        ("Date*", "activity_date", "Date", True),
        ("Title of FLD*", "oft_title", "Text", True),
        ("Crop Variety*", "oft_crop_variety", "Text", True),
        ("No. of Farmers*", "oft_farmer_count", "Integer", True),
        ("Technical Assessment*", "oft_technical_assessment", "Text", True),
        ("Area*", "oft_area", "Text", True),
        ("Farmer Name*", "farmer_name", "Text", True),
        ("Mobile No.*", "contact_number", "Mobile", True),
        ("Scientist*", "oft_farmer_scientist", "Text", True),
        ("Purpose*", "oft_farmer_purpose", "Text", True),
        ("District*", "oft_farmer_district", "Text", True),
        ("Tehsil*", "oft_farmer_tehsil", "Text", True),
        ("Category*", "oft_farmer_category", "Choice", True),
    ],
    "Training Programmes": [
        ("Training Type*", "training_type", "Choice", True),
        ("Department*", "department_id", "Reference", True),
        ("Start Date*", "activity_date", "Date", True),
        ("End Date*", "training_end_date", "Date", True),
        ("Title*", "training_title", "Text", True),
        ("Clientele*", "clientele", "Choice", True),
        ("Venue*", "venue", "Text", True),
        ("Venue Mode*", "venue_is_offline", "Choice", True),
        ("No. of Farmers*", "training_farmer_count", "Integer", True),
        ("Description", "description", "Text", False),
        ("Remarks", "remarks", "Text", False),
        ("Farmer Name*", "farmer_name", "Text", True),
        ("Mobile No.*", "contact_number", "Mobile", True),
        ("Scientist*", "training_farmer_scientist", "Text", True),
        ("Purpose*", "training_farmer_purpose", "Text", True),
        ("Category*", "training_farmer_category", "Choice", True),
        ("District*", "training_farmer_district", "Text", True),
        ("Tehsil*", "training_farmer_tehsil", "Text", True),
    ],
    "Vocational Training Programmes": [
        ("Training Type*", "training_type", "Choice", True),
        ("Department*", "department_id", "Reference", True),
        ("Start Date*", "activity_date", "Date", True),
        ("End Date*", "training_end_date", "Date", True),
        ("Title*", "training_title", "Text", True),
        ("Clientele*", "clientele", "Choice", True),
        ("Venue*", "venue", "Text", True),
        ("Venue Mode*", "venue_is_offline", "Choice", True),
        ("No. of Farmers*", "training_farmer_count", "Integer", True),
        ("Description", "description", "Text", False),
        ("Remarks", "remarks", "Text", False),
        ("Farmer Name*", "farmer_name", "Text", True),
        ("Mobile No.*", "contact_number", "Mobile", True),
        ("Scientist*", "training_farmer_scientist", "Text", True),
        ("Purpose*", "training_farmer_purpose", "Text", True),
        ("Category*", "training_farmer_category", "Choice", True),
        ("District*", "training_farmer_district", "Text", True),
        ("Tehsil*", "training_farmer_tehsil", "Text", True),
    ],
    "Extension Activities": [
        ("Activity*", "activity_type", "Text", True),
        ("Date*", "activity_date", "Date", True),
        ("Venue*", "extension_venue", "Text", True),
        ("Location*", "extension_location", "Text", True),
        ("Department*", "extension_department", "Text", True),
        ("Purpose of Visit*", "extension_purpose", "Text", True),
        ("No. of Farmers*", "extension_farmer_count", "Integer", True),
    ],
    "Other Extension Activities": [
        ("Activity*", "activity_type", "Text", True),
        ("Date*", "activity_date", "Date", True),
        ("Title of Show*", "other_extension_title", "Text", True),
    ],
}


class DocumentDropFrame(QFrame):
    def __init__(self, on_document_selected):
        super().__init__()
        self.on_document_selected = on_document_selected
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.on_document_selected(urls[0].toLocalFile())


class DocumentDigitizationWidget(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.document_path = None
        self.original_pixmap = None
        self.rotation = 0
        self.zoom = 1.0
        self.page_count = 0
        self.current_page = 1
        self.record_fields = {}
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        header_card = QFrame()
        header_card.setObjectName("Card")
        header_layout = QVBoxLayout(header_card)
        title_row = QHBoxLayout()
        title = QLabel("AI-Powered Document Digitization")
        title.setObjectName("CardTitle")
        title_row.addWidget(title)
        title_row.addStretch(1)
        status = QLabel("Under Development")
        status.setObjectName("HintLabel")
        title_row.addWidget(status)
        subtitle = QLabel(
            "Convert scanned documents and images into structured digital records using intelligent OCR technology."
        )
        subtitle.setWordWrap(True)
        info = QLabel(
            "The document digitization interface is available. AI-based text recognition and automated field "
            "extraction are currently under development."
        )
        info.setWordWrap(True)
        header_layout.addLayout(title_row)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(info)
        root.addWidget(header_card)

        config_card = QFrame()
        config_card.setObjectName("Card")
        config_layout = QHBoxLayout(config_card)
        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES)
        self.category_combo.currentTextChanged.connect(self._category_changed)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Marathi", "English and Marathi"])
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("PaddleOCR – Offline (Planned)")
        self.engine_combo.addItem("Google Cloud Vision – Online (Planned)")
        self.engine_combo.setCurrentIndex(0)
        self.engine_combo.setEnabled(False)
        for label, widget in (
            ("Document Category", self.category_combo),
            ("Document Language", self.language_combo),
            ("OCR Engine", self.engine_combo),
        ):
            column = QVBoxLayout()
            column.addWidget(QLabel(label))
            column.addWidget(widget)
            config_layout.addLayout(column)
        root.addWidget(config_card)

        upload_card = QFrame()
        upload_card.setObjectName("Card")
        upload_layout = QHBoxLayout(upload_card)
        self.drop_area = DocumentDropFrame(self._select_document)
        self.drop_area.setMinimumHeight(72)
        drop_layout = QVBoxLayout(self.drop_area)
        self.document_hint = QLabel("No document selected. Upload an image or PDF to begin.")
        self.document_hint.setAlignment(Qt.AlignCenter)
        self.document_hint.setWordWrap(True)
        drop_layout.addWidget(self.document_hint)

        button_column = QVBoxLayout()
        upload_button = QPushButton("Upload Document")
        browse_button = QPushButton("Browse Files")
        replace_button = QPushButton("Replace Document")
        remove_button = QPushButton("Remove Document")
        upload_button.clicked.connect(lambda: self._select_document())
        browse_button.clicked.connect(lambda: self._select_document())
        replace_button.clicked.connect(lambda: self._select_document())
        remove_button.clicked.connect(self.reset_document)
        for button in (upload_button, browse_button, replace_button, remove_button):
            button_column.addWidget(button)

        upload_layout.addWidget(self.drop_area, 3)
        upload_layout.addLayout(button_column, 1)
        root.addWidget(upload_card)

        workflow_card = QFrame()
        workflow_card.setObjectName("Card")
        workflow_layout = QVBoxLayout(workflow_card)
        workflow_layout.addWidget(QLabel("Processing Workflow"))
        steps_layout = QHBoxLayout()
        self.workflow_labels = []
        steps = [
            "1. Document Upload",
            "2. Image Preprocessing",
            "3. Text Recognition",
            "4. Field Mapping",
            "5. Data Validation",
            "6. Staff Verification",
            "7. Database Storage",
        ]
        for index, text in enumerate(steps):
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setFrameShape(QFrame.StyledPanel)
            label.setMinimumHeight(38)
            steps_layout.addWidget(label)
            self.workflow_labels.append(label)
        workflow_layout.addLayout(steps_layout)
        root.addWidget(workflow_card)

        action_row = QHBoxLayout()
        self.extract_button = QPushButton("Extract Text")
        self.map_button = QPushButton("Map Fields")
        self.validate_button = QPushButton("Validate Data")
        self.duplicates_button = QPushButton("Review Duplicates")
        self.verify_button = QPushButton("Verify Record")
        self.save_button = QPushButton("Save Record")
        self.reset_button = QPushButton("Reset")
        for button in (
            self.extract_button,
            self.map_button,
            self.duplicates_button,
            self.verify_button,
            self.save_button,
        ):
            button.setEnabled(False)
        self.validate_button.clicked.connect(self._validate_ui)
        self.reset_button.clicked.connect(self.reset_all)
        for button in (
            self.extract_button,
            self.map_button,
            self.validate_button,
            self.duplicates_button,
            self.verify_button,
            self.save_button,
            self.reset_button,
        ):
            action_row.addWidget(button)
        action_row.addStretch(1)
        root.addLayout(action_row)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        left_card = QFrame()
        left_card.setObjectName("Card")
        left_layout = QVBoxLayout(left_card)
        left_layout.addWidget(QLabel("Original Document"))

        preview_toolbar = QHBoxLayout()
        for text, callback in (
            ("Zoom In", self.zoom_in),
            ("Zoom Out", self.zoom_out),
            ("Fit", self.fit_preview),
            ("Rotate Left", self.rotate_left),
            ("Rotate Right", self.rotate_right),
            ("Previous", self.previous_page),
            ("Next", self.next_page),
        ):
            button = QPushButton(text)
            button.clicked.connect(callback)
            preview_toolbar.addWidget(button)
        preview_toolbar.addStretch(1)
        left_layout.addLayout(preview_toolbar)

        self.preview_label = QLabel("No document selected")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(360, 360)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        preview_scroll.setAlignment(Qt.AlignCenter)
        preview_scroll.setWidget(self.preview_label)
        left_layout.addWidget(preview_scroll, 1)
        self.page_indicator = QLabel("Page 0 / 0")
        left_layout.addWidget(self.page_indicator)
        splitter.addWidget(left_card)

        right_card = QFrame()
        right_card.setObjectName("Card")
        right_layout = QVBoxLayout(right_card)
        self.tabs = QTabWidget()

        extracted_page = QWidget()
        extracted_layout = QVBoxLayout(extracted_page)
        self.extracted_text = QTextEdit()
        self.extracted_text.setReadOnly(True)
        self.extracted_text.setPlainText(
            "Recognized text will appear here after the OCR engine is integrated."
        )
        extracted_layout.addWidget(self.extracted_text)
        self.tabs.addTab(extracted_page, "Extracted Text")

        mapping_page = QWidget()
        mapping_layout = QVBoxLayout(mapping_page)
        self.mapping_table = QTableWidget(0, 6)
        self.mapping_table.setHorizontalHeaderLabels(
            ["Database Field", "Extracted Value", "Data Type", "Required", "Confidence", "Validation Status"]
        )
        self.mapping_table.setAlternatingRowColors(True)
        self.mapping_table.setShowGrid(False)
        self.mapping_table.verticalHeader().setVisible(False)
        self.mapping_table.horizontalHeader().setStretchLastSection(True)
        mapping_layout.addWidget(self.mapping_table)
        self.tabs.addTab(mapping_page, "Field Mapping")

        record_page = QWidget()
        record_scroll = QScrollArea()
        record_scroll.setWidgetResizable(True)
        record_scroll.setFrameShape(QFrame.NoFrame)
        self.record_form = QWidget()
        self.record_form_layout = QVBoxLayout(self.record_form)
        self.record_form_layout.setContentsMargins(8, 8, 8, 8)
        record_scroll.setWidget(self.record_form)
        record_layout = QVBoxLayout(record_page)
        record_layout.setContentsMargins(0, 0, 0, 0)
        record_layout.addWidget(record_scroll)
        self.tabs.addTab(record_page, "Record Preview")

        right_layout.addWidget(self.tabs)
        splitter.addWidget(right_card)
        splitter.setSizes([600, 600])
        root.addWidget(splitter, 1)

        self._category_changed(self.category_combo.currentText())
        self._update_workflow()

    def _category_changed(self, category):
        self._build_mapping_table(category)
        self._build_record_preview(category)
        self.document_hint.setText(
            "No document selected. Upload an image or PDF to begin."
            if not self.document_path
            else Path(self.document_path).name
            + f"\nCategory: {category}  |  Language: {self.language_combo.currentText()}"
        )

    def _build_mapping_table(self, category):
        fields = FIELD_REGISTRY.get(category, [])
        self.mapping_table.setRowCount(len(fields))
        for row, (label, database_field, data_type, required) in enumerate(fields):
            values = [
                database_field,
                "",
                data_type,
                "Yes" if required else "No",
                "N/A",
                "Pending",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 1:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                self.mapping_table.setItem(row, column, item)

    def _build_record_preview(self, category):
        while self.record_form_layout.count():
            item = self.record_form_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.record_fields = {}
        form = QVBoxLayout()
        for label, database_field, data_type, required in FIELD_REGISTRY.get(category, []):
            field_row = QHBoxLayout()
            field_label = QLabel(label)
            field_label.setMinimumWidth(180)
            if data_type in ("Choice", "Reference"):
                widget = QComboBox()
                if data_type == "Choice":
                    if database_field == "season":
                        widget.addItems(["Kharif", "Rabi"])
                    elif database_field == "clientele":
                        widget.addItems(["PF", "RY", "EF"])
                    elif database_field == "training_type":
                        widget.addItems(["Regular", "Vocational", "Sponsored"])
                    elif database_field == "venue_is_offline":
                        widget.addItems(["On", "Off"])
                    elif database_field == "oft_farmer_category":
                        widget.addItem("Select or enter category")
                        widget.setEditable(True)
                    else:
                        widget.setEditable(True)
                else:
                    widget.setEditable(True)
            elif data_type == "Text" and len(label) > 35:
                widget = QTextEdit()
                widget.setFixedHeight(65)
            elif data_type == "Date":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(label.rstrip("*"))
            self.record_fields[database_field] = widget
            field_row.addWidget(field_label)
            field_row.addWidget(widget, 1)
            row_widget = QWidget()
            row_widget.setLayout(field_row)
            form.addWidget(row_widget)
        form.addStretch(1)
        container = QWidget()
        container.setLayout(form)
        self.record_form_layout.addWidget(container)

    def _select_document(self, path=None):
        if not path:
            from PyQt5.QtWidgets import QFileDialog

            path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Document",
                "",
                "Supported Documents (*.jpg *.jpeg *.png *.pdf);;All Files (*.*)",
            )
        if not path:
            return
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            QMessageBox.warning(self, "Invalid File", "The selected document path is not available.")
            return
        suffix = Path(path).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".pdf"}:
            QMessageBox.warning(
                self,
                "Unsupported Format",
                "Supported formats are JPG, JPEG, PNG and PDF.",
            )
            return
        try:
            if suffix == ".pdf":
                with open(path, "rb") as pdf_file:
                    header = pdf_file.read(5)
                if header != b"%PDF-":
                    raise ValueError("The file is not a readable PDF.")
                self.original_pixmap = None
                self.page_count = self._count_pdf_pages(path)
                self.preview_label.setText(
                    "PDF preview is unavailable. The original PDF will remain unchanged."
                )
                self.preview_label.setPixmap(QPixmap())
            else:
                pixmap = QPixmap(path)
                if pixmap.isNull():
                    raise ValueError("The image could not be decoded.")
                self.original_pixmap = pixmap
                self.rotation = 0
                self.zoom = 1.0
                self.page_count = 1
                self._update_preview()
            self.document_path = path
            self.current_page = 1
            self._update_document_info()
            self._update_workflow()
        except Exception as exc:
            QMessageBox.warning(self, "Unreadable Document", str(exc))

    def _count_pdf_pages(self, path):
        try:
            data = Path(path).read_bytes()
            matches = re.findall(rb"/Type\s*/Page\b", data)
            if matches:
                return len(matches)
            matches = re.findall(rb"/Count\s+(\d+)", data)
            if matches:
                return max(int(value) for value in matches)
        except (OSError, ValueError):
            pass
        return 0

    def _update_document_info(self):
        if not self.document_path:
            return
        path = Path(self.document_path)
        size = path.stat().st_size
        if size < 1024:
            size_text = f"{size} bytes"
        else:
            size_text = f"{size / 1024:.1f} KB"
        page_text = str(self.page_count) if self.page_count else "Unknown"
        self.document_hint.setText(
            f"{path.name}\nFormat: {path.suffix.lower().lstrip('.').upper()}  |  "
            f"Size: {size_text}  |  Pages: {page_text}\n"
            f"Category: {self.category_combo.currentText()}  |  "
            f"Language: {self.language_combo.currentText()}"
        )
        self.page_indicator.setText(f"Page {self.current_page if self.page_count else 0} / {self.page_count}")

    def reset_document(self):
        self.document_path = None
        self.original_pixmap = None
        self.page_count = 0
        self.current_page = 1
        self.rotation = 0
        self.zoom = 1.0
        self.preview_label.clear()
        self.preview_label.setText("No document selected")
        self.document_hint.setText("No document selected. Upload an image or PDF to begin.")
        self.page_indicator.setText("Page 0 / 0")
        self._update_workflow()

    def reset_all(self):
        self.reset_document()
        self.category_combo.setCurrentIndex(0)
        self.language_combo.setCurrentIndex(0)
        self.extracted_text.setPlainText(
            "Recognized text will appear here after the OCR engine is integrated."
        )

    def _update_workflow(self):
        completed = 0
        if self.document_path:
            completed = 1
        for index, label in enumerate(self.workflow_labels):
            if index < completed:
                label.setStyleSheet(
                    "background-color: #217a45; color: #ffffff; border: 1px solid #186338;"
                )
            elif index == completed:
                if index == 1:
                    label.setStyleSheet(
                        "background-color: #d9f0de; color: #176b32; border: 1px solid #9dccaa;"
                    )
            else:
                label.setStyleSheet(
                    "background-color: #eef6ef; color: #5d7264; border: 1px solid #c9e3cd;"
                )

    def _validate_ui(self):
        missing = []
        for label, database_field, data_type, required in FIELD_REGISTRY.get(
            self.category_combo.currentText(), []
        ):
            if not required:
                continue
            widget = self.record_fields.get(database_field)
            if isinstance(widget, QLineEdit):
                value = widget.text().strip()
            elif isinstance(widget, QTextEdit):
                value = widget.toPlainText().strip()
            elif isinstance(widget, QComboBox):
                value = widget.currentText().strip()
            elif isinstance(widget, QDateEdit):
                value = widget.date().toString("yyyy-MM-dd")
            else:
                value = ""
            if not value:
                missing.append(label)
        if missing:
            QMessageBox.warning(
                self,
                "Validation",
                "The following required fields are empty:\n- " + "\n- ".join(missing),
            )
        else:
            QMessageBox.information(
                self,
                "Validation",
                "The editable UI fields are complete. OCR and database validation are not performed in this version.",
            )

    def _update_preview(self):
        if not self.original_pixmap:
            return
        rotated = self.original_pixmap.transformed(
            QTransform().rotate(self.rotation),
            Qt.SmoothTransformation,
        )
        available_width = max(100, int(self.preview_label.width() * self.zoom))
        available_height = max(100, int(self.preview_label.height() * self.zoom))
        scaled = rotated.scaled(
            available_width,
            available_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)

    def zoom_in(self):
        self.zoom = min(4.0, self.zoom * 1.25)
        self._update_preview()

    def zoom_out(self):
        self.zoom = max(0.25, self.zoom / 1.25)
        self._update_preview()

    def fit_preview(self):
        self.zoom = 1.0
        self._update_preview()

    def rotate_left(self):
        self.rotation = (self.rotation - 90) % 360
        self._update_preview()

    def rotate_right(self):
        self.rotation = (self.rotation + 90) % 360
        self._update_preview()

    def previous_page(self):
        if self.page_count > 0:
            self.current_page = max(1, self.current_page - 1)
            self._update_document_info()

    def next_page(self):
        if self.page_count > 0:
            self.current_page = min(self.page_count, self.current_page + 1)
            self._update_document_info()
