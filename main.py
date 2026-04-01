import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox

from controllers.auth_controller import AuthController
from database.init_db import create_tables, seed_departments, test_connection
from ui.login_window import LoginWindow
from ui.styles import APP_STYLE


def _configure_logging() -> None:
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "kvk_app.log"

    handler = RotatingFileHandler(log_file, maxBytes=1_048_576, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def _handle_unexpected_exception(exc_type, exc_value, exc_tb) -> None:
    # Keep Ctrl+C behavior untouched in console mode.
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return

    logging.critical("Unhandled exception:\n%s", "".join(traceback.format_exception(exc_type, exc_value, exc_tb)))
    app = QApplication.instance() or QApplication(sys.argv)
    QMessageBox.critical(
        None,
        "Application Error",
        "An unexpected error occurred. The issue has been logged in logs/kvk_app.log.",
    )


def bootstrap_database() -> bool:
    """Initializes database objects and default master/admin data."""
    try:
        test_connection()
        create_tables()
        seed_departments()
        AuthController.ensure_default_admin()
        # Sync primary key sequences to prevent duplicate key errors
        from services.backup_service import BackupService
        BackupService._sync_primary_key_sequences()
        return True
    except Exception as exc:
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "Database Error",
            "Could not initialize PostgreSQL. Check .env connection settings.\n\n"
            f"Technical details: {exc}",
        )
        return False


def main() -> None:
    _configure_logging()
    sys.excepthook = _handle_unexpected_exception

    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    if not bootstrap_database():
        sys.exit(1)

    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
