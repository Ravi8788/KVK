"""Small spinning indicator used while the desktop app waits on work."""

from contextlib import contextmanager

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class Spinner(QWidget):
    """Green loading circle drawn with a rotating arc."""

    def __init__(self, parent=None, diameter=48):
        super().__init__(parent)
        self._angle = 0
        self.setFixedSize(diameter, diameter)
        timer = QTimer(self)
        timer.timeout.connect(self._turn)
        timer.start(30)

    def _turn(self) -> None:
        self._angle = (self._angle + 24) % 360
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(6, 6, -6, -6)
        track = QPen(QColor("#d7eadc"))
        track.setWidth(4)
        track.setCapStyle(Qt.RoundCap)
        painter.setPen(track)
        painter.drawEllipse(rect)
        arc = QPen(QColor("#217a45"))
        arc.setWidth(4)
        arc.setCapStyle(Qt.RoundCap)
        painter.setPen(arc)
        painter.drawArc(rect, int(-self._angle * 16), 110 * 16)


class LoadingWindow(QWidget):
    """Standalone loading card for startup and sign-in."""

    def __init__(self, message="Loading"):
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(280, 168)
        self.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #d5e8d8; border-radius: 8px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(12)
        layout.addWidget(Spinner(self), 0, Qt.AlignCenter)
        self.message = QLabel(message)
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setStyleSheet("color: #1c2b1e; font-size: 14px; border: none;")
        layout.addWidget(self.message)

    def set_message(self, message: str) -> None:
        self.message.setText(message)
        QApplication.processEvents()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        self.move(area.center().x() - self.width() // 2, area.center().y() - self.height() // 2)


class LoadingOverlay(QWidget):
    """Covers a window while a search, report, or import is running."""

    def __init__(self, parent, message="Loading"):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(244, 250, 245, 220);")
        layout = QVBoxLayout(self)
        layout.addStretch(1)
        layout.addWidget(Spinner(self), 0, Qt.AlignCenter)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #176b32; font-size: 14px; font-weight: 600; background: transparent;")
        layout.addWidget(label)
        layout.addStretch(1)

    def present(self) -> None:
        parent = self.parentWidget()
        if parent is not None:
            self.setGeometry(parent.rect())
        self.show()
        self.raise_()
        QApplication.processEvents()


@contextmanager
def busy(parent, message="Loading"):
    """Shows the loading circle for the duration of a block of work."""
    host = parent.window() if parent is not None else None
    overlay = LoadingOverlay(host, message) if host is not None else None
    if overlay is not None:
        overlay.present()
    try:
        yield
    finally:
        if overlay is not None:
            overlay.hide()
            overlay.deleteLater()
            QApplication.processEvents()
