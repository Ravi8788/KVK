from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from ui.activity_form_widget import ActivityFormWidget
from ui.backup_widget import BackupWidget
from ui.reports_widget import ReportsWidget
from ui.user_management_widget import UserManagementWidget


MODULES = [
    "Visitor Farmers",
    "On Farm Testing (OFT)",
    "Front Line Demonstrations (FLD)",
    "Training Programmes",
    "Vocational Training Programmes",
    "Extension Activities",
    "Other Extension Activities",
    "Reports",
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

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("KVK Database Management System")
        self.setMinimumSize(1200, 760)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.nav_buttons = []
        top_nav = self._build_top_nav()
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(16, 16, 16, 16)

        for module_name in MODULES:
            self.stack.addWidget(self._build_module_page(module_name))

        root_layout.addWidget(top_nav, 0)
        root_layout.addWidget(self.stack, 1)

        self.setCentralWidget(root)
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

        subtitle = QLabel(f"Signed in: {self.user.full_name} ({self.user.role.upper()})")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)
        header_layout.addStretch(1)
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
            button = HoverButton(module_name)
            button.setObjectName("NavButton")
            button.setMinimumHeight(40)
            text_width = QFontMetrics(button.font()).horizontalAdvance(module_name)
            button.setFixedWidth(max(170, min(380, text_width + 70)))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            button.setIcon(self._icon_for_module(module_name))
            if self.user.role == "staff" and module_name in ADMIN_ONLY_MODULES:
                button.setEnabled(False)
            button.clicked.connect(lambda checked=False, i=idx: self._on_module_clicked(i))
            button.hovered.connect(lambda i=idx: self._on_module_hovered(i))
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

    def _on_module_hovered(self, index: int) -> None:
        if MODULES[index] == "Exit":
            return
        if self.user.role == "staff" and MODULES[index] in ADMIN_ONLY_MODULES:
            return
        self.stack.setCurrentIndex(index)
        self._set_active_module(index)

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
        description = QLabel(
            "This is the starter page for this module. In Phase 2, this page will host the full form, table, and actions."
        )
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
        if module_name == "Reports":
            return ReportsWidget(self.user)
        if module_name == "Backup & Restore":
            return BackupWidget(self.user)
        if module_name == "User Management":
            if self.user.role != "admin":
                return self._build_placeholder_page("Access denied. Only admin can use User Management.")
            return UserManagementWidget(self.user)
        if module_name == "Exit":
            return self._build_placeholder_page("Use sidebar Exit to close application.")
        return self._build_placeholder_page(module_name)

    def _on_module_clicked(self, index: int) -> None:
        if MODULES[index] == "Exit":
            self.close()
            return
        self.stack.setCurrentIndex(index)
        self._set_active_module(index)


class HoverButton(QPushButton):
    hovered = pyqtSignal()

    def enterEvent(self, event) -> None:
        self.hovered.emit()
        super().enterEvent(event)
