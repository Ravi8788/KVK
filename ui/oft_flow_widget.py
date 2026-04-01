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
    """Step-by-step OFT flow: Department -> Type -> Season -> Load Form -> Data Entry."""

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

        # Workflow state that is passed to final form step.
        self.selected_department_label = ""
        self.selected_department_db = ""
        self.selected_type = ""
        self.selected_season = ""

        self._build_ui()
        self._go_to_department_step()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        self.flow_label = QLabel("OFT -> Department -> Type -> Season -> Load Form")
        self.flow_label.setObjectName("CardTitle")
        root.addWidget(self.flow_label)

        self.state_label = QLabel("Select Department")
        root.addWidget(self.state_label)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_department_page())
        self.stack.addWidget(self._build_type_page())
        self.stack.addWidget(self._build_season_page())
        self.stack.addWidget(self._build_load_form_page())
        self.stack.addWidget(self._build_data_form_page())
        root.addWidget(self.stack)

    def _build_department_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        title = QLabel("Step 1: Select Department")
        title.setObjectName("CardTitle")
        card_layout.addWidget(title)

        btn_grid = QGridLayout()
        departments = list(self.DEPARTMENT_LABEL_TO_DB.keys())
        for idx, dept_label in enumerate(departments):
            button = QPushButton(dept_label)
            button.setMinimumHeight(60)
            button.clicked.connect(lambda checked=False, d=dept_label: self._select_department(d))
            row = idx // 2
            col = idx % 2
            btn_grid.addWidget(button, row, col)

        card_layout.addLayout(btn_grid)
        layout.addWidget(card)
        return page

    def _build_type_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        title = QLabel("Step 2: Select Type")
        title.setObjectName("CardTitle")
        card_layout.addWidget(title)

        buttons = QHBoxLayout()
        assessment_btn = QPushButton("Assessment")
        refinement_btn = QPushButton("Refinement")
        assessment_btn.setMinimumHeight(60)
        refinement_btn.setMinimumHeight(60)
        assessment_btn.clicked.connect(lambda: self._select_type("Assessment"))
        refinement_btn.clicked.connect(lambda: self._select_type("Refinement"))

        buttons.addWidget(assessment_btn)
        buttons.addWidget(refinement_btn)
        card_layout.addLayout(buttons)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self._go_to_department_step)
        card_layout.addWidget(back_btn)

        layout.addWidget(card)
        return page

    def _build_season_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        title = QLabel("Step 3: Select Season")
        title.setObjectName("CardTitle")
        card_layout.addWidget(title)

        buttons = QHBoxLayout()
        kharif_btn = QPushButton("Kharif")
        rabi_btn = QPushButton("Rabi")
        kharif_btn.setMinimumHeight(60)
        rabi_btn.setMinimumHeight(60)
        kharif_btn.clicked.connect(lambda: self._select_season("Kharif"))
        rabi_btn.clicked.connect(lambda: self._select_season("Rabi"))
        buttons.addWidget(kharif_btn)
        buttons.addWidget(rabi_btn)
        card_layout.addLayout(buttons)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self._go_to_type_step)
        card_layout.addWidget(back_btn)

        layout.addWidget(card)
        return page

    def _build_load_form_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        title = QLabel("Step 4: Load Data Entry Form")
        title.setObjectName("CardTitle")
        card_layout.addWidget(title)

        self.load_summary_label = QLabel("")
        self.load_summary_label.setWordWrap(True)
        card_layout.addWidget(self.load_summary_label)

        load_btn = QPushButton("Load Form")
        load_btn.setMinimumHeight(60)
        load_btn.clicked.connect(self._go_to_form_step)
        card_layout.addWidget(load_btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self._go_to_season_step)
        card_layout.addWidget(back_btn)

        layout.addWidget(card)
        return page

    def _build_data_form_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)

        title = QLabel("OFT Data Entry Form")
        title.setObjectName("CardTitle")
        card_layout.addWidget(title)

        form_grid = QGridLayout()

        self.farmer_name_input = QLineEdit()
        self.village_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.department_display = QLineEdit()
        self.department_display.setReadOnly(True)
        self.type_display = QLineEdit()
        self.type_display.setReadOnly(True)
        self.season_display = QLineEdit()
        self.season_display.setReadOnly(True)

        self.remarks_input = QTextEdit()
        self.remarks_input.setFixedHeight(90)

        form_grid.addWidget(QLabel("Farmer Name*"), 0, 0)
        form_grid.addWidget(self.farmer_name_input, 0, 1)

        form_grid.addWidget(QLabel("Village*"), 1, 0)
        form_grid.addWidget(self.village_input, 1, 1)

        form_grid.addWidget(QLabel("Date*"), 2, 0)
        form_grid.addWidget(self.date_input, 2, 1)

        form_grid.addWidget(QLabel("Department"), 3, 0)
        form_grid.addWidget(self.department_display, 3, 1)

        form_grid.addWidget(QLabel("Type"), 4, 0)
        form_grid.addWidget(self.type_display, 4, 1)

        form_grid.addWidget(QLabel("Season"), 5, 0)
        form_grid.addWidget(self.season_display, 5, 1)

        form_grid.addWidget(QLabel("Remarks"), 6, 0)
        form_grid.addWidget(self.remarks_input, 6, 1)

        card_layout.addLayout(form_grid)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        reset_btn = QPushButton("Reset")
        back_btn = QPushButton("Back")

        save_btn.clicked.connect(self._save_form)
        reset_btn.clicked.connect(self._reset_form)
        back_btn.clicked.connect(self._go_to_load_form_step)

        btn_row.addWidget(save_btn)
        btn_row.addWidget(reset_btn)
        btn_row.addWidget(back_btn)
        btn_row.addStretch(1)

        card_layout.addLayout(btn_row)
        layout.addWidget(card)
        return page

    def _update_state_label(self) -> None:
        parts = ["OFT"]
        if self.selected_department_label:
            parts.append(self.selected_department_label)
        if self.selected_type:
            parts.append(self.selected_type)
        if self.selected_season:
            parts.append(self.selected_season)
        self.state_label.setText(" -> ".join(parts))

    def _select_department(self, department_label: str) -> None:
        self.selected_department_label = department_label
        self.selected_department_db = self.DEPARTMENT_LABEL_TO_DB[department_label]
        self._update_state_label()
        self._go_to_type_step()

    def _select_type(self, selected_type: str) -> None:
        self.selected_type = selected_type
        self._update_state_label()
        self._go_to_season_step()

    def _select_season(self, selected_season: str) -> None:
        self.selected_season = selected_season
        self._update_state_label()
        self.load_summary_label.setText(
            f"Department: {self.selected_department_label}\n"
            f"Type: {self.selected_type}\n"
            f"Season: {self.selected_season}"
        )
        self._go_to_load_form_step()

    def _go_to_department_step(self) -> None:
        self.stack.setCurrentIndex(0)

    def _go_to_type_step(self) -> None:
        self.stack.setCurrentIndex(1)

    def _go_to_season_step(self) -> None:
        self.stack.setCurrentIndex(2)

    def _go_to_load_form_step(self) -> None:
        self.stack.setCurrentIndex(3)

    def _go_to_form_step(self) -> None:
        self.department_display.setText(self.selected_department_label)
        self.type_display.setText(self.selected_type)
        self.season_display.setText(self.selected_season)
        self.stack.setCurrentIndex(4)

    def _reset_form(self) -> None:
        self.farmer_name_input.clear()
        self.village_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.remarks_input.clear()

    def _resolve_department(self, session) -> Tuple[int, str]:
        department = session.query(Department).filter(Department.name == self.selected_department_db).first()
        if department is None:
            raise ValueError(f"Department '{self.selected_department_db}' not found in database.")
        return department.id, department.name

    def _get_or_create_farmer(self, session, farmer_name: str, village: str) -> Farmer:
        farmer = (
            session.query(Farmer)
            .filter(Farmer.farmer_name == farmer_name, Farmer.village == village)
            .order_by(Farmer.id.desc())
            .first()
        )
        if farmer:
            return farmer

        # Contact number is not part of this guided OFT form, so a placeholder is used.
        farmer = Farmer(
            farmer_name=farmer_name,
            village=village,
            contact_number="NA",
        )
        session.add(farmer)
        session.flush()
        return farmer

    def _save_form(self) -> None:
        farmer_name = self.farmer_name_input.text().strip()
        village = self.village_input.text().strip()
        remarks = self.remarks_input.toPlainText().strip()

        if not farmer_name or not village:
            QMessageBox.warning(self, "Validation", "Farmer Name and Village are required.")
            return

        session = SessionLocal()
        try:
            department_id, department_name = self._resolve_department(session)
            farmer = self._get_or_create_farmer(session, farmer_name, village)

            activity = Activity(
                module_type=self.MODULE_DB_VALUE,
                farmer_id=farmer.id,
                department_id=department_id,
                season=self.selected_season,
                activity_type=self.selected_type,
                activity_date=self.date_input.date().toPyDate(),
                description=f"OFT flow entry ({self.selected_type})",
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
                details=f"Saved OFT flow record for {farmer_name} ({department_name})",
            )

            QMessageBox.information(self, "Saved", "OFT record saved successfully.")
            self._reset_form()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Could not save OFT record: {exc}")
        finally:
            session.close()
