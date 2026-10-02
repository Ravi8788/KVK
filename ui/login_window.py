from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from controllers.auth_controller import AuthController
from ui.dashboard_window import DashboardWindow
from ui.loading_overlay import LoadingWindow


class LoginWindow(QMainWindow):
    """Username and password login for admin and staff users."""

    def __init__(self):
        super().__init__()
        self.dashboard = None
        self.setWindowTitle("KVK System")
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(48, 40, 48, 40)

        card = QFrame()
        card.setObjectName("LoginCard")
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 28)
        card_layout.setSpacing(10)

        eyebrow = QLabel("KRISHI VIDNYANKENDRA")
        eyebrow.setObjectName("HintLabel")
        title = QLabel("Sign in")
        title.setObjectName("TitleLabel")
        subtitle = QLabel("Database management for farmer activities, trainings, and reports.")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)

        username_label = QLabel("Username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setClearButtonEnabled(True)

        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self._on_login_clicked)

        login_btn = QPushButton("Sign in")
        login_btn.setMinimumHeight(40)
        login_btn.setDefault(True)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self._on_login_clicked)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("SecondaryButton")
        close_btn.setMinimumHeight(40)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)

        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        hint = QLabel("Use the account issued by your KVK office.")
        hint.setObjectName("HintLabel")
        hint.setWordWrap(True)

        card_layout.addWidget(eyebrow)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(12)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(8)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(close_btn)
        card_layout.addStretch(1)
        card_layout.addWidget(hint)

        layout.addStretch(1)
        layout.addWidget(card, 0, Qt.AlignCenter)
        layout.addStretch(1)
        self.setCentralWidget(root)
        self.username_input.setFocus()

    def _show_error(self, message: str) -> None:
        self.error_label.setText(message)
        self.error_label.show()

    def _on_login_clicked(self) -> None:
        self.error_label.hide()
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self._show_error("Enter both username and password.")
            return

        loader = LoadingWindow("Signing in")
        loader.show()
        QApplication.processEvents()
        try:
            user = AuthController.login(username, password)
        except Exception:
            loader.close()
            self._show_error("The login service is unavailable. Check the database connection and try again.")
            return

        if user is None:
            loader.close()
            self._show_error("Those credentials were not accepted. Check the username and password.")
            return

        loader.set_message("Loading the workspace")
        self.dashboard = DashboardWindow(user, on_logout=self._on_logout)
        loader.close()
        self.dashboard.showMaximized()
        self.hide()

    def _on_logout(self) -> None:
        self.password_input.clear()
        self.error_label.hide()
        self.showFullScreen()
        self.activateWindow()
