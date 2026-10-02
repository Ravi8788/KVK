from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.user_service import UserService


class UserManagementWidget(QWidget):
    """Admin-only user creation and active status management."""

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self._build_ui()
        self._load_users()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        title = QLabel("User Management")
        title.setObjectName("CardTitle")
        root.addWidget(title)

        if self.current_user.role != "admin":
            warning = QLabel("Only admin users can manage users.")
            root.addWidget(warning)
            return

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        self.username_input = QLineEdit()
        self.full_name_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["staff", "admin"])

        form.addRow("Username*", self.username_input)
        form.addRow("Full Name*", self.full_name_input)
        form.addRow("Password*", self.password_input)
        form.addRow("Role*", self.role_combo)

        row = QHBoxLayout()
        add_user_btn = QPushButton("Create user")
        add_user_btn.setCursor(Qt.PointingHandCursor)
        add_user_btn.clicked.connect(self._create_user)
        deactivate_btn = QPushButton("Deactivate selected")
        activate_btn = QPushButton("Activate selected")
        deactivate_btn.setObjectName("SecondaryButton")
        activate_btn.setObjectName("SecondaryButton")
        deactivate_btn.setCursor(Qt.PointingHandCursor)
        activate_btn.setCursor(Qt.PointingHandCursor)
        deactivate_btn.clicked.connect(lambda: self._set_status_for_selected(False))
        activate_btn.clicked.connect(lambda: self._set_status_for_selected(True))

        row.addWidget(add_user_btn)
        row.addWidget(activate_btn)
        row.addWidget(deactivate_btn)
        row.addStretch(1)

        form_layout.addLayout(form)
        form_layout.addLayout(row)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Role", "Active"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)

        root.addWidget(form_card)
        root.addWidget(self.table)

    def _create_user(self) -> None:
        username = self.username_input.text().strip()
        full_name = self.full_name_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combo.currentText()

        if not username or not full_name or not password:
            QMessageBox.warning(self, "Validation", "All required fields must be filled.")
            return

        try:
            UserService.create_user(
                username=username,
                full_name=full_name,
                password=password,
                role=role,
                created_by=self.current_user.id,
            )
            QMessageBox.information(self, "Success", "User created successfully.")
            self.username_input.clear()
            self.full_name_input.clear()
            self.password_input.clear()
            self._load_users()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _load_users(self) -> None:
        if self.current_user.role != "admin":
            return

        users = UserService.list_users()
        self.table.setRowCount(0)
        for i, user in enumerate(users):
            self.table.insertRow(i)
            values = [
                user.id,
                user.username,
                user.full_name,
                user.role,
                "Yes" if user.is_active else "No",
            ]
            for col, value in enumerate(values):
                self.table.setItem(i, col, QTableWidgetItem(str(value)))

    def _set_status_for_selected(self, status: bool) -> None:
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Selection", "Select a user row first.")
            return

        user_id_item = self.table.item(selected, 0)
        if user_id_item is None:
            return

        user_id = int(user_id_item.text())
        try:
            UserService.set_active_status(user_id, status, self.current_user.id)
            QMessageBox.information(self, "Success", "User status updated.")
            self._load_users()
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
