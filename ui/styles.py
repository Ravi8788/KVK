APP_STYLE = """
QMainWindow, QWidget {
    background-color: #f8fff8;
    color: #1f2d1f;
    font-family: 'Segoe UI';
    font-size: 13px;
}

QFrame#Sidebar {
    background-color: #ffffff;
    border-right: 2px solid #dcebdc;
}

QFrame#TopBar {
    background-color: #ffffff;
    border-bottom: 2px solid #dcebdc;
}

QLabel#TitleLabel {
    color: #1a6f34;
    font-size: 20px;
    font-weight: 700;
}

QPushButton {
    background-color: #2e8b57;
    color: white;
    border-radius: 8px;
    padding: 10px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #246f46;
}

QPushButton#SidebarButton {
    text-align: left;
    background-color: #e9f6ea;
    color: #1d4a2f;
    border: 1px solid #c8e5cc;
    padding: 12px;
}

QPushButton#SidebarButton:hover {
    background-color: #d8eedb;
}

QPushButton#NavButton {
    text-align: left;
    background-color: #e9f6ea;
    color: #1d4a2f;
    border: 1px solid #c8e5cc;
    border-radius: 8px;
    padding: 8px 10px;
    font-weight: 600;
}

QPushButton#NavButton:hover {
    background-color: #d8eedb;
}

QPushButton#NavButton[active="true"] {
    background-color: #2e8b57;
    color: #ffffff;
    border: 1px solid #2b7e50;
}

QLineEdit, QComboBox, QDateEdit, QTextEdit {
    background: #ffffff;
    border: 1px solid #b6d7b9;
    border-radius: 6px;
    padding: 6px;
}

QLabel#CardTitle {
    font-size: 16px;
    font-weight: 700;
    color: #225d36;
}

QLabel#AnalyticsValue {
    color: #1a6f34;
    font-size: 24px;
    font-weight: 700;
}

QLabel#AnalyticsStatus {
    color: #5b705f;
    padding: 4px 8px;
}

QTableWidget {
    background: #ffffff;
    alternate-background-color: #f2f8f2;
    gridline-color: #dcebdc;
    border: 1px solid #dcebdc;
}

QHeaderView::section {
    background: #e9f6ea;
    color: #225d36;
    border: 0;
    border-bottom: 1px solid #c8e5cc;
    padding: 7px;
    font-weight: 600;
}

QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #dcebdc;
    border-radius: 10px;
}
"""
