from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controllers.auth_controller import AuthController
from ui.dashboard_window import DashboardWindow


class LoginWindow(QMainWindow):
    """Simple username/password login for admin/staff users."""

    def __init__(self):
        super().__init__()
        self.dashboard = None
        self.setWindowTitle("KVK Login")
        self.setFixedSize(540, 360)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)

        title = QLabel("Krishi Vigyan Kendra")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("Database Management System")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(44)
        login_btn.clicked.connect(self._on_login_clicked)

        info = QLabel("Default first-run admin: admin / admin123")
        info.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(login_btn)
        card_layout.addStretch(1)
        card_layout.addWidget(info)

        layout.addWidget(card)
        self.setCentralWidget(root)

    def _on_login_clicked(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Validation", "Username and password are required.")
            return

        try:
            user = AuthController.login(username, password)
            if user is None:
                QMessageBox.critical(self, "Login Failed", "Login failed. Check credentials and try again.")
                return
        except Exception:
            QMessageBox.critical(self, "Login Error", "Login service is temporarily unavailable. Please try again.")
            return

        self.dashboard = DashboardWindow(user)
        self.dashboard.show()
        self.close()
