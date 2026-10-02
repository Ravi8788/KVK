import os

from PyQt5.QtCore import QEvent, Qt, QTimer
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from ui.activity_form_widget import ActivityFormWidget
from analytics.analytics_widget import AnalyticsWidget
from ui.backup_widget import BackupWidget
from ui.reports_widget import ReportsWidget
from ui.smart_widgets import (
    AlertsWidget,
    CalendarWidget,
    DataQualityWidget,
    DuplicateWidget,
    ImportWidget,
    OverviewWidget,
    ScrollPage,
    SearchDialog,
    SettingsWidget,
    VillageWidget,
    YearCompareWidget,
)
from ui.user_management_widget import UserManagementWidget
from services.audit_service import AuditService
from services.smart_service import SettingsService


MODULES = [
    "Overview",
    "Visitor Farmers",
    "On Farm Testing (OFT)",
    "Front Line Demonstrations (FLD)",
    "Training Programmes",
    "Vocational Training Programmes",
    "Extension Activities",
    "Other Extension Activities",
    "Analytics",
    "Reports",
    "Data Quality",
    "Duplicates",
    "Import",
    "Calendar",
    "Village Analysis",
    "Year Comparison",
    "Alerts",
    "Settings",
    "Backup & Restore",
    "User Management",
    "Exit",
]

ACTIVITY_MODULES = {
    "Visitor Farmers",
    "On Farm Testing (OFT)",
    "Front Line Demonstrations (FLD)",
    "Training Programmes",
    "Vocational Training Programmes",
    "Extension Activities",
    "Other Extension Activities",
}

STAFF_READONLY_MODULES = {
    "On Farm Testing (OFT)",
    "Front Line Demonstrations (FLD)",
    "Extension Activities",
}

ADMIN_ONLY_MODULES = {
    "User Management",
}


class DashboardWindow(QMainWindow):
    """Basic dashboard shell with sidebar and module page switching."""

    def __init__(self, user, on_logout=None):
        super().__init__()
        self.user = user
        self.on_logout = on_logout
        self._logging_out = False
        self._timeout_ms = 0
        self.setWindowTitle("KVK Database Management System")
        self.setMinimumSize(1200, 760)
        self._idle = QTimer(self)
        self._idle.setSingleShot(True)
        self._idle.timeout.connect(self._session_expired)
        self._build_ui()
        self.apply_session_timeout()
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.nav_buttons = []
        top_nav = self._build_top_nav()
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(16, 16, 16, 16)

        app = QApplication.instance()
        for module_name in MODULES:
            self.stack.addWidget(self._build_module_page(module_name))
            if app is not None:
                app.processEvents()

        root_layout.addWidget(top_nav, 0)
        root_layout.addWidget(self.stack, 1)

        self.setCentralWidget(root)
        database_name = os.getenv("DB_NAME", "kvk_db")
        self.statusBar().showMessage(f"Connected to {database_name}    ·    Signed in as {self.user.username}")
        self._set_active_module(0)

    def _build_top_nav(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("TopBar")

        outer_layout = QVBoxLayout(frame)
        outer_layout.setContentsMargins(10, 8, 10, 8)
        outer_layout.setSpacing(8)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(4, 2, 4, 2)

        title = QLabel("KVK System")
        title.setObjectName("TitleLabel")
        header_layout.addWidget(title)

        self.module_label = QLabel(MODULES[0])
        self.module_label.setObjectName("ModuleLabel")
        header_layout.addWidget(self.module_label)

        subtitle = QLabel(f"{self.user.full_name}  ·  {self.user.role.title()}")
        subtitle.setObjectName("SubtitleLabel")
        header_layout.addWidget(subtitle)
        header_layout.addStretch(1)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search name, ID number, mobile, village")
        self.search_input.setFixedWidth(280)
        self.search_input.returnPressed.connect(self._open_search)
        search_btn = QPushButton("Search")
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.clicked.connect(self._open_search)
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("SecondaryButton")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(search_btn)
        header_layout.addWidget(logout_btn)
        outer_layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)

        nav_container = QWidget()
        layout = QHBoxLayout(nav_container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        for idx, module_name in enumerate(MODULES):
            button = QPushButton(module_name)
            button.setObjectName("NavButton")
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(36)
            text_width = QFontMetrics(button.font()).horizontalAdvance(module_name)
            button.setFixedWidth(max(150, min(280, text_width + 48)))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            button.setIcon(self._icon_for_module(module_name))
            if self.user.role == "staff" and module_name in ADMIN_ONLY_MODULES:
                button.setEnabled(False)
                button.setToolTip("Only an administrator can open User Management.")
            button.clicked.connect(lambda checked=False, i=idx: self._on_module_clicked(i))
            layout.addWidget(button)
            self.nav_buttons.append(button)

        layout.addStretch(1)
        scroll.setWidget(nav_container)
        outer_layout.addWidget(scroll)

        return frame

    def _set_active_module(self, index: int) -> None:
        for btn_index, button in enumerate(self.nav_buttons):
            button.setProperty("active", btn_index == index)
            button.style().unpolish(button)
            button.style().polish(button)
        if MODULES[index] != "Exit":
            self.module_label.setText(MODULES[index])

    def _icon_for_module(self, module_name: str):
        style = QApplication.style()
        if module_name == "Reports":
            return style.standardIcon(QStyle.SP_FileDialogDetailedView)
        if module_name == "Backup & Restore":
            return style.standardIcon(QStyle.SP_DriveFDIcon)
        if module_name == "User Management":
            return style.standardIcon(QStyle.SP_DirHomeIcon)
        if module_name == "Exit":
            return style.standardIcon(QStyle.SP_DialogCloseButton)
        return style.standardIcon(QStyle.SP_FileIcon)

    def _build_placeholder_page(self, module_name: str) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(module_name)
        title.setObjectName("CardTitle")
        description = QLabel("This section is not available for the signed-in account.")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignTop)

        card_layout.addWidget(title)
        card_layout.addSpacing(8)
        card_layout.addWidget(description)

        page_layout.addWidget(card)
        page_layout.addStretch(1)
        return page

    def _build_module_page(self, module_name: str) -> QWidget:
        if module_name in ACTIVITY_MODULES:
            read_only = self.user.role == "staff" and module_name in STAFF_READONLY_MODULES
            return ActivityFormWidget(module_name, self.user, read_only=read_only)
        if module_name == "Overview":
            return ScrollPage(OverviewWidget(self._open_module))
        if module_name == "Reports":
            return ReportsWidget(self.user)
        if module_name == "Analytics":
            return AnalyticsWidget(self.user)
        if module_name == "Data Quality":
            return ScrollPage(DataQualityWidget(self._open_module))
        if module_name == "Duplicates":
            return ScrollPage(DuplicateWidget(self.user, self._open_module))
        if module_name == "Import":
            return ScrollPage(ImportWidget(self.user))
        if module_name == "Calendar":
            return CalendarWidget(self._open_module)
        if module_name == "Village Analysis":
            return ScrollPage(VillageWidget())
        if module_name == "Year Comparison":
            return ScrollPage(YearCompareWidget())
        if module_name == "Alerts":
            return ScrollPage(AlertsWidget(self._open_module))
        if module_name == "Settings":
            return ScrollPage(SettingsWidget(self.user))
        if module_name == "Backup & Restore":
            return BackupWidget(self.user)
        if module_name == "User Management":
            if self.user.role != "admin":
                return self._build_placeholder_page("Access denied. Only admin can use User Management.")
            return UserManagementWidget(self.user)
        if module_name == "Exit":
            return self._build_placeholder_page("Exit")
        return self._build_placeholder_page(module_name)

    def _on_module_clicked(self, index: int) -> None:
        if MODULES[index] == "Exit":
            answer = QMessageBox.question(
                self,
                "Exit",
                "Close KVK System?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer == QMessageBox.Yes:
                self.close()
            return
        self.stack.setCurrentIndex(index)
        self._set_active_module(index)

    def _open_module(self, name: str, search_text: str = "") -> None:
        if name not in MODULES or name == "Exit":
            return
        index = MODULES.index(name)
        self._on_module_clicked(index)
        page = self.stack.widget(index)
        target = page
        if hasattr(page, "widget") and callable(page.widget):
            try:
                nested = page.widget()
                if nested is not None:
                    target = nested
            except Exception:
                target = page
        text = (search_text or "").strip()
        if text and hasattr(target, "focus_search"):
            target.focus_search(text)

    def _open_search(self) -> None:
        text = self.search_input.text().strip()
        if len(text) < 1 or (len(text) < 2 and not text.isdigit()):
            QMessageBox.information(self, "Search", "Type a name, or the farmer ID number such as 48.")
            return
        SearchDialog(text, self._open_module, self).exec_()

    def apply_session_timeout(self) -> None:
        try:
            minutes = int(SettingsService.get("session_timeout_minutes") or "0")
        except ValueError:
            minutes = 30
        if minutes <= 0:
            self._timeout_ms = 0
            self._idle.stop()
            return
        self._timeout_ms = minutes * 60 * 1000
        self._idle.start(self._timeout_ms)

    def eventFilter(self, obj, event):
        if self._timeout_ms and event.type() in (QEvent.MouseButtonPress, QEvent.KeyPress):
            self._idle.start(self._timeout_ms)
        return super().eventFilter(obj, event)

    def _session_expired(self) -> None:
        QMessageBox.information(self, "Session", "The session timed out. Sign in again.")
        self.logout()

    def logout(self) -> None:
        if self._logging_out:
            return
        self._logging_out = True
        self._idle.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        AuditService.log_action(self.user.id, "logout", "Authentication", self.user.id, "User logged out")
        if self.on_logout:
            self.on_logout()
        self.close()
