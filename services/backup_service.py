import os
import shutil
import subprocess
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.session import engine
from services.audit_service import AuditService

load_dotenv()


class BackupService:
    """Creates SQL backups and restores database using PostgreSQL tools."""

    @staticmethod
    def _resolve_pg_tool(tool_name: str) -> str:
        """Resolves pg_dump/psql path from PATH, env override, or common install directories."""
        executable_name = f"{tool_name}.exe" if os.name == "nt" else tool_name

        # 1) PATH lookup
        from_path = shutil.which(tool_name) or shutil.which(executable_name)
        if from_path:
            return from_path

        # 2) Optional explicit bin directory in .env
        pg_bin_dir = os.getenv("PG_BIN_DIR", "").strip()
        if pg_bin_dir:
            candidate = os.path.join(pg_bin_dir, executable_name)
            if os.path.exists(candidate):
                return candidate

        # 3) Common Windows PostgreSQL install paths
        if os.name == "nt":
            base_dirs = [
                os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "PostgreSQL"),
                os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "PostgreSQL"),
            ]
            for base_dir in base_dirs:
                if not os.path.isdir(base_dir):
                    continue
                for version in ["18", "17", "16", "15", "14", "13", "12"]:
                    candidate = os.path.join(base_dir, version, "bin", executable_name)
                    if os.path.exists(candidate):
                        return candidate

        raise RuntimeError(
            f"{tool_name} not found. Install PostgreSQL client tools or set PG_BIN_DIR in .env to PostgreSQL bin folder."
        )

    @staticmethod
    def _db_env() -> dict:
        env = os.environ.copy()
        env["PGPASSWORD"] = os.getenv("DB_PASSWORD", "postgres")
        return env

    @staticmethod
    def _conn_values() -> dict:
        return {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "dbname": os.getenv("DB_NAME", "kvk_db"),
            "user": os.getenv("DB_USER", "postgres"),
        }

    @staticmethod
    def _is_database_initialized() -> bool:
        """Check if database has user data (non-empty users, farmers, or activities tables).
        Returns True if database has data, False if empty/crashed.
        """
        try:
            with engine.connect() as connection:
                # Check for user data (exclude bootstrap admin user if only one exists)
                user_count = connection.execute(text("SELECT COUNT(*) FROM public.users")).scalar_one()
                # Check for farmer records
                farmer_count = connection.execute(text("SELECT COUNT(*) FROM public.farmers")).scalar_one()
                # Check for activity records
                activity_count = connection.execute(text("SELECT COUNT(*) FROM public.activities")).scalar_one()
                
                # Database is considered initialized if it has any non-system data
                # (More than 1 user, or any farmers/activities)
                return user_count > 1 or farmer_count > 0 or activity_count > 0
        except Exception:
            # If we can't check, assume initialized to prevent data loss
            return True

    @staticmethod
    def _sync_primary_key_sequences() -> None:
        """Resyncs SERIAL/BIGSERIAL sequences to max(id) after restore/import."""
        table_names = ["departments", "users", "farmers", "activities", "reports", "audit_logs"]
        with engine.begin() as connection:
            for table_name in table_names:
                connection.execute(
                    text(
                        f"""
                        SELECT setval(
                            pg_get_serial_sequence('public.{table_name}', 'id'),
                            COALESCE((SELECT MAX(id) FROM public.{table_name}), 1),
                            true
                        )
                        """
                    )
                )

    @staticmethod
    def validate_backup_file(sql_file_path: str) -> None:
        if not os.path.isfile(sql_file_path):
            raise ValueError("Backup file was not found.")
        if not sql_file_path.lower().endswith(".sql"):
            raise ValueError("Choose a PostgreSQL .sql backup file.")
        if os.path.getsize(sql_file_path) < 50:
            raise ValueError("The backup file looks empty.")
        with open(sql_file_path, "r", encoding="utf-8", errors="replace") as handle:
            head = handle.read(800).lower()
        if "postgresql" not in head and "create table" not in head and "pg_dump" not in head:
            raise ValueError("This file does not look like a PostgreSQL backup.")

    @staticmethod
    def backup_database(output_dir: str, current_user_id: int) -> str:
        os.makedirs(output_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(output_dir, f"kvk_backup_{stamp}.sql")

        conn = BackupService._conn_values()
        pg_dump_path = BackupService._resolve_pg_tool("pg_dump")
        cmd = [
            pg_dump_path,
            "-h",
            conn["host"],
            "-p",
            conn["port"],
            "-U",
            conn["user"],
            "-d",
            conn["dbname"],
            "-F",
            "p",
            "-f",
            file_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, env=BackupService._db_env())
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Backup failed")

        AuditService.log_action(
            user_id=current_user_id,
            action="backup_database",
            module_type="Backup",
            details=f"Backup generated: {file_path}",
        )
        return file_path

    @staticmethod
    def restore_database(sql_file_path: str, current_user_id: int) -> None:
        BackupService.validate_backup_file(sql_file_path)
        if not os.path.exists(sql_file_path):
            raise FileNotFoundError("SQL file not found")

        # Safety check: Only allow restore on empty/crashed databases to prevent duplicate data
        if BackupService._is_database_initialized():
            raise RuntimeError(
                "Database already contains data. Restore can only be performed on an empty or crashed database. "
                "To restore over existing data, first backup current data and manually clear the database."
            )

        conn = BackupService._conn_values()
        psql_path = BackupService._resolve_pg_tool("psql")
        cmd = [
            psql_path,
            "-h",
            conn["host"],
            "-p",
            conn["port"],
            "-U",
            conn["user"],
            "-d",
            conn["dbname"],
            "-f",
            sql_file_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, env=BackupService._db_env())
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Restore failed")

        BackupService._sync_primary_key_sequences()

        try:
            AuditService.log_action(
                user_id=current_user_id,
                action="restore_database",
                module_type="Backup",
                details=f"Restore executed from: {sql_file_path}",
            )
        except SQLAlchemyError:
            # Restore success should not fail because of audit log insert issues.
            pass

    @staticmethod
    def get_database_metadata() -> dict:
        """Returns key database metadata to confirm restore target."""
        with engine.connect() as connection:
            db_name = connection.execute(text("SELECT current_database()")).scalar_one()
            db_version = connection.execute(text("SELECT version()")).scalar_one()
            table_count = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    """
                )
            ).scalar_one()

        conn = BackupService._conn_values()
        return {
            "host": conn["host"],
            "port": conn["port"],
            "database": db_name,
            "version": db_version,
            "table_count": table_count,
        }

    @staticmethod
    def safe_restore_with_prebackup(sql_file_path: str, backup_dir: str, current_user_id: int) -> str:
        """Creates a safety backup before restore and returns safety backup path.
        This is only safe if database is empty/crashed. Will raise error if data exists.
        """
        # Check if database has data - if yes, create safety backup before attempting restore
        if BackupService._is_database_initialized():
            safety_backup = BackupService.backup_database(backup_dir, current_user_id)
            raise RuntimeError(
                f"Database contains existing data. Safety backup created at: {safety_backup}. "
                "Restore cannot proceed. Archive the backup and manually clear the database if you want to restore."
            )
        else:
            # Database is empty/crashed, safe to restore directly without pre-backup
            BackupService.restore_database(sql_file_path, current_user_id)
            AuditService.log_action(
                user_id=current_user_id,
                action="safe_restore_on_crashed_db",
                module_type="Backup",
                details=f"Restore executed on empty/crashed database from: {sql_file_path}",
            )
            return sql_file_path
