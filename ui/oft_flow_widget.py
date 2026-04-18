from datetime import datetime
from typing import Dict, Tuple

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from database.session import SessionLocal
from models.entities import Activity, Department, Farmer
from services.audit_service import AuditService


class OFTFlowWidget(QWidget):
    """OFT flow: Department & Activity Type selection -> Data Entry Form."""

    MODULE_DB_VALUE = "On Farm Testing (OFT)"

    DEPARTMENT_LABEL_TO_DB = {
        "Agronomy": "Agronomy",
        "Horticulture": "Horticulture",
        "Plant Protection": "Plant Protection",
        "Veterinary Science": "Veterinary Science",
        "Soil Science": "Soil Science",
        "Home Science": "Home Science",
        "Agri Extension": "Agricultural Extension",
    }

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        # Workflow state
        self.selected_department_label = ""
        self.selected_department_db = ""
        self.selected_type = ""

        self._build_ui()
        self._go_to_department_step()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        self.flow_label = QLabel("OFT Data Entry Form")
        self.flow_label.setObjectName("CardTitle")
        root.addWidget(self.flow_label)

        self.state_label = QLabel("Select Department and Activity Type")
        root.addWidget(self.state_label)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_selection_page())
        self.stack.addWidget(self._build_data_form_page())
        root.addWidget(self.stack)

    def _build_selection_page(self) -> QWidget:
        """Step 1: Select Department and Activity Type side by side."""
        page = QWidget()
        layout = QVBoxLayout(page)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        title = QLabel("Step 1: Select Department and Activity Type")
        title.setObjectName("CardTitle")
        card_layout.addWidget(title)

        # Department Section
        dept_label = QLabel("Department*")
        dept_label.setObjectName("SectionLabel")
        card_layout.addWidget(dept_label)
        
        btn_grid = QGridLayout()
        departments = list(self.DEPARTMENT_LABEL_TO_DB.keys())
        for idx, dept_label_text in enumerate(departments):
            button = QPushButton(dept_label_text)
            button.setMinimumHeight(60)
            button.clicked.connect(lambda checked=False, d=dept_label_text: self._select_department(d))
            row = idx // 2
            col = idx % 2
            btn_grid.addWidget(button, row, col)

        card_layout.addLayout(btn_grid)
        
        # Activity Type Section
        activity_label = QLabel("Activity Type*")
        activity_label.setObjectName("SectionLabel")
        card_layout.addWidget(activity_label)
        
        type_buttons = QHBoxLayout()
        assessment_btn = QPushButton("Assessment")
        refinement_btn = QPushButton("Refinement")
        assessment_btn.setMinimumHeight(60)
        refinement_btn.setMinimumHeight(60)
        assessment_btn.clicked.connect(lambda: self._select_type("Assessment"))
        refinement_btn.clicked.connect(lambda: self._select_type("Refinement"))
        type_buttons.addWidget(assessment_btn)
        type_buttons.addWidget(refinement_btn)
        card_layout.addLayout(type_buttons)
        
        layout.addWidget(card)
        layout.addStretch()
        return page


    def _build_data_form_page(self) -> QWidget:
        """Step 2: Data Entry Form with all required fields."""
        page = QWidget()
        layout = QVBoxLayout(page)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        title = QLabel("Step 2: Enter Activity Details")
        title.setObjectName("CardTitle")
        card_layout.addWidget(title)

        form_grid = QGridLayout()

        self.farmer_name_input = QLineEdit()
        self.village_input = QLineEdit()
        self.contact_number_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(80)

        self.department_display = QLineEdit()
        self.department_display.setReadOnly(True)
        self.type_display = QLineEdit()
        self.type_display.setReadOnly(True)

        self.remarks_input = QTextEdit()
        self.remarks_input.setFixedHeight(80)

        form_grid.addWidget(QLabel("Farmer Name*"), 0, 0)
        form_grid.addWidget(self.farmer_name_input, 0, 1)

        form_grid.addWidget(QLabel("Village*"), 1, 0)
        form_grid.addWidget(self.village_input, 1, 1)

        form_grid.addWidget(QLabel("Contact Number*"), 2, 0)
        form_grid.addWidget(self.contact_number_input, 2, 1)

        form_grid.addWidget(QLabel("Date*"), 3, 0)
        form_grid.addWidget(self.date_input, 3, 1)

        form_grid.addWidget(QLabel("Department"), 4, 0)
        form_grid.addWidget(self.department_display, 4, 1)

        form_grid.addWidget(QLabel("Activity Type"), 5, 0)
        form_grid.addWidget(self.type_display, 5, 1)

        form_grid.addWidget(QLabel("Description*"), 6, 0)
        form_grid.addWidget(self.description_input, 6, 1)

        form_grid.addWidget(QLabel("Remarks"), 7, 0)
        form_grid.addWidget(self.remarks_input, 7, 1)

        card_layout.addLayout(form_grid)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        reset_btn = QPushButton("Reset")
        back_btn = QPushButton("Back")

        save_btn.clicked.connect(self._save_form)
        reset_btn.clicked.connect(self._reset_form)
        back_btn.clicked.connect(self._go_to_selection_step)

        btn_row.addWidget(save_btn)
        btn_row.addWidget(reset_btn)
        btn_row.addWidget(back_btn)
        btn_row.addStretch(1)

        card_layout.addLayout(btn_row)
        layout.addWidget(card)
        layout.addStretch()
        return page

    def _update_state_label(self) -> None:
        parts = ["OFT"]
        if self.selected_department_label:
            parts.append(self.selected_department_label)
        if self.selected_type:
            parts.append(self.selected_type)
        self.state_label.setText(" -> ".join(parts))

    def _select_department(self, department_label: str) -> None:
        self.selected_department_label = department_label
        self.selected_department_db = self.DEPARTMENT_LABEL_TO_DB[department_label]
        self._update_state_label()

    def _select_type(self, selected_type: str) -> None:
        self.selected_type = selected_type
        self._update_state_label()

        self._go_to_form_step()

    def _go_to_selection_step(self) -> None:
        self.selected_department_label = ""
        self.selected_department_db = ""
        self.selected_type = ""
        self._update_state_label()
        self.stack.setCurrentIndex(0)

    def _go_to_form_step(self) -> None:
        self.department_display.setText(self.selected_department_label)
        self.type_display.setText(self.selected_type)
        self.stack.setCurrentIndex(1)

    def _reset_form(self) -> None:
        self.farmer_name_input.clear()
        self.village_input.clear()
        self.contact_number_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.description_input.clear()
        self.remarks_input.clear()

    def _resolve_department(self, session) -> Tuple[int, str]:
        department = session.query(Department).filter(Department.name == self.selected_department_db).first()
        if department is None:
            raise ValueError(f"Department '{self.selected_department_db}' not found in database.")
        return department.id, department.name

    def _get_or_create_farmer(self, session, farmer_name: str, village: str, contact_number: str) -> Farmer:
        farmer = (
            session.query(Farmer)
            .filter(Farmer.farmer_name == farmer_name, Farmer.village == village)
            .order_by(Farmer.id.desc())
            .first()
        )
        if farmer:
            return farmer

        farmer = Farmer(
            farmer_name=farmer_name,
            village=village,
            contact_number=contact_number,
        )
        session.add(farmer)
        session.flush()
        return farmer

    def _save_form(self) -> None:
        farmer_name = self.farmer_name_input.text().strip()
        village = self.village_input.text().strip()
        contact_number = self.contact_number_input.text().strip()
        description = self.description_input.toPlainText().strip()
        remarks = self.remarks_input.toPlainText().strip()

        if not farmer_name or not village or not contact_number or not description:
            QMessageBox.warning(
                self, 
                "Validation", 
                "Farmer Name, Village, Contact Number, and Description are required."
            )
            return

        session = SessionLocal()
        try:
            department_id, department_name = self._resolve_department(session)
            farmer = self._get_or_create_farmer(session, farmer_name, village, contact_number)

            activity = Activity(
                module_type=self.MODULE_DB_VALUE,
                farmer_id=farmer.id,
                department_id=department_id,
                season="",
                activity_type=self.selected_type,
                activity_date=self.date_input.date().toPyDate(),
                description=description,
                remarks=remarks,
                created_by=self.current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(activity)
            session.commit()

            AuditService.log_action(
                user_id=self.current_user.id,
                action="create_oft_flow_activity",
                module_type=self.MODULE_DB_VALUE,
                record_id=activity.id,
                details=f"Saved OFT flow record for {farmer_name} ({department_name}) - {self.selected_type}",
            )

            QMessageBox.information(self, "Saved", "OFT record saved successfully.")
            self._reset_form()
            self._go_to_selection_step()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Could not save OFT record: {exc}")
        finally:
            session.close()
