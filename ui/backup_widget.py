import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.backup_service import BackupService
from services.smart_service import SettingsService, last_backup


class BackupWidget(QWidget):
    """Backup and restore controls for PostgreSQL SQL files."""

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        title = QLabel("Backup and Restore")
        title.setObjectName("CardTitle")
        root.addWidget(title)

        intro = QLabel("Save a full SQL copy of the database. Restore replaces data only when the database is empty, and it asks for confirmation first.")
        intro.setObjectName("SubtitleLabel")
        intro.setWordWrap(True)
        root.addWidget(intro)

        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        row = QHBoxLayout()
        backup_btn = QPushButton("Backup database")
        self.restore_btn = QPushButton("Restore database")
        backup_btn.setCursor(Qt.PointingHandCursor)
        self.restore_btn.setCursor(Qt.PointingHandCursor)
        self.restore_btn.setObjectName("SecondaryButton")
        backup_btn.clicked.connect(self._backup)
        self.restore_btn.clicked.connect(self._restore)

        row.addWidget(backup_btn)
        row.addWidget(self.restore_btn)
        row.addStretch(1)

        if self.current_user.role != "admin":
            self.restore_btn.setEnabled(False)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setPlaceholderText("Backup and restore activity will appear here.")
        self.logs.setMinimumHeight(220)
        if self.current_user.role != "admin":
            self.logs.append("Restore is restricted to admin users.")

        layout.addLayout(row)
        layout.addWidget(self.logs)
        root.addWidget(card)
        self._refresh_status()

    def _refresh_status(self) -> None:
        last = last_backup()
        if last is None:
            self.status_label.setText("Last backup: not yet taken. Status: no backup recorded.")
            return
        self.status_label.setText(f"Last backup: {last['created_at']:%d-%m-%Y %H:%M}    Status: {last['status']}")

    def _backup(self) -> None:
        start_dir = SettingsService.get("backup_folder") or os.path.join(os.getcwd(), "backups")
        output_dir = QFileDialog.getExistingDirectory(self, "Select Backup Folder", start_dir)
        if not output_dir:
            return
        try:
            backup_path = BackupService.backup_database(output_dir, self.current_user.id)
            self.logs.append(f"Backup successful: {backup_path}")
            self._refresh_status()
            QMessageBox.information(self, "Backup", f"Backup completed:\n{backup_path}")
        except Exception as exc:
            QMessageBox.critical(self, "Backup Error", str(exc))

    def _restore(self) -> None:
        if self.current_user.role != "admin":
            QMessageBox.warning(self, "Access Denied", "Only admin users can restore database backups.")
            return

        # Warn user about restore requirements
        warning = QMessageBox.warning(
            self,
            "Restore Database - Important",
            "Restore can ONLY be performed on an EMPTY/CRASHED database.\n\nIf database has existing data, restore will be blocked to prevent duplicate entries.\n\nDo you want to proceed?",
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        if warning != QMessageBox.Ok:
            return

        sql_file, _ = QFileDialog.getOpenFileName(self, "Select SQL Backup", "", "SQL Files (*.sql)")
        if not sql_file:
            return

        try:
            BackupService.validate_backup_file(sql_file)
        except Exception as exc:
            QMessageBox.critical(self, "Backup File", str(exc))
            return

        try:
            metadata = BackupService.get_database_metadata()
        except Exception as exc:
            QMessageBox.critical(self, "Metadata Error", f"Could not read database metadata: {exc}")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Restore",
            "Restore target details:\n"
            f"Host: {metadata['host']}:{metadata['port']}\n"
            f"Database: {metadata['database']}\n"
            f"Tables in public schema: {metadata['table_count']}\n\n"
            "WARNING: A restore can replace the data in this database. Continue only if this database should be replaced from the backup file.",
        )
        if confirm != QMessageBox.Yes:
            return

        token, ok = QInputDialog.getText(
            self,
            "Type Confirmation",
            "Type RESTORE to confirm:",
        )
        if not ok or token.strip() != "RESTORE":
            QMessageBox.information(self, "Cancelled", "Restore cancelled.")
            return

        try:
            safety_dir = os.path.join(os.getcwd(), "backups", "pre_restore")
            result = BackupService.safe_restore_with_prebackup(sql_file, safety_dir, self.current_user.id)
            self.logs.append(f"Restore successful from: {sql_file}")
            QMessageBox.information(
                self,
                "Restore Complete",
                f"Database restored successfully.\nSource: {result}",
            )
        except Exception as exc:
            self.logs.append(f"Restore failed: {str(exc)}")
            QMessageBox.critical(self, "Restore Error", str(exc))
