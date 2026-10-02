APP_STYLE = """
QMainWindow, QMainWindow > QWidget, QDialog {
    background-color: #f4faf5;
}

QWidget {
    color: #1c2b1e;
    font-family: "Segoe UI";
    font-size: 13px;
}

QFrame#TopBar {
    background-color: #ffffff;
    border-bottom: 1px solid #d5e8d8;
}

QLabel#TitleLabel {
    color: #176b32;
    font-size: 20px;
    font-weight: 700;
}

QLabel#SubtitleLabel {
    color: #4d6454;
    font-size: 13px;
}

QLabel#ModuleLabel {
    color: #176b32;
    font-size: 15px;
    font-weight: 700;
}

QLabel#HintLabel {
    color: #5d7264;
    font-size: 12px;
}

QLabel#ErrorLabel {
    color: #9b2c2c;
    font-weight: 600;
}

QPushButton {
    background-color: #217a45;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #1a6538;
}

QPushButton:pressed {
    background-color: #14512c;
}

QPushButton:disabled {
    background-color: #d5e3d8;
    color: #6d7f72;
}

QPushButton#NavButton {
    text-align: left;
    background-color: #eef6ef;
    color: #1d4a2f;
    border: 1px solid #c9e3cd;
    border-radius: 6px;
    padding: 8px 12px;
    font-weight: 600;
}

QPushButton#NavButton:hover {
    background-color: #e0f2e3;
    border-color: #9dccaa;
}

QPushButton#NavButton:pressed {
    background-color: #d3ead8;
}

QPushButton#NavButton[active="true"] {
    background-color: #217a45;
    color: #ffffff;
    border: 1px solid #186338;
}

QPushButton#NavButton:disabled {
    background-color: #f3f6f3;
    color: #8aa092;
    border: 1px solid #e1ebe2;
}

QPushButton#SecondaryButton {
    background-color: #ffffff;
    color: #1d4a2f;
    border: 1px solid #b7d4bb;
}

QPushButton#SecondaryButton:hover {
    background-color: #eef6ef;
}

QPushButton#SecondaryButton:pressed {
    background-color: #e0f2e3;
}

QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {
    background: #ffffff;
    border: 1px solid #c5dcc8;
    border-radius: 6px;
    padding: 6px 8px;
    min-height: 20px;
    selection-background-color: #cfe8d4;
    selection-color: #14301c;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border: 1px solid #217a45;
}

QLineEdit:disabled, QComboBox:disabled, QDateEdit:disabled, QTextEdit:disabled {
    background: #f3f6f3;
    color: #6d7f72;
}

QComboBox::drop-down, QDateEdit::drop-down {
    border: none;
    width: 22px;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #c5dcc8;
    selection-background-color: #d9f0de;
    selection-color: #14301c;
    outline: 0;
    padding: 4px;
}

QTextEdit {
    padding: 8px;
}

QLabel#CardTitle {
    font-size: 18px;
    font-weight: 700;
    color: #176b32;
}

QLabel#AnalyticsValue {
    color: #176b32;
    font-size: 22px;
    font-weight: 700;
}

QLabel#AnalyticsStatus {
    color: #5d7264;
    padding: 2px 0;
}

QTableWidget {
    background: #ffffff;
    alternate-background-color: #f3faf4;
    border: 1px solid #d5e8d8;
    border-radius: 6px;
    gridline-color: transparent;
    selection-background-color: #d9f0de;
    selection-color: #14301c;
}

QTableWidget::item {
    padding: 6px 8px;
    border: none;
}

QTableWidget::item:selected {
    background: #d9f0de;
    color: #14301c;
}

QHeaderView::section {
    background: #e7f5ea;
    color: #1d4a2f;
    border: none;
    border-bottom: 1px solid #c9e3cd;
    border-right: 1px solid #e3f0e5;
    padding: 8px;
    font-weight: 600;
}

QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #d5e8d8;
    border-radius: 10px;
}

QFrame#LoginCard {
    background-color: #ffffff;
    border: 1px solid #d5e8d8;
    border-radius: 12px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px 2px 4px 0;
}

QScrollBar::handle:vertical {
    background: #b7d0bb;
    min-height: 28px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #8fb596;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 0 4px 2px 4px;
}

QScrollBar::handle:horizontal {
    background: #b7d0bb;
    min-width: 28px;
    border-radius: 5px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QTabWidget::pane {
    border: 1px solid #d5e8d8;
    background: #ffffff;
    border-radius: 8px;
    top: -1px;
}

QTabBar::tab {
    background: #eef6ef;
    color: #1d4a2f;
    padding: 8px 16px;
    border: 1px solid #c9e3cd;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
}

QTabBar::tab:selected {
    background: #217a45;
    color: #ffffff;
    border-color: #186338;
}

QTabBar::tab:hover:!selected {
    background: #e0f2e3;
}

QRadioButton, QCheckBox {
    spacing: 8px;
}

QStatusBar {
    background: #ffffff;
    color: #3e5646;
    border-top: 1px solid #d5e8d8;
}

QToolTip {
    background: #1c2b1e;
    color: #ffffff;
    border: none;
    padding: 6px 8px;
}
"""
