from sqlalchemy import text

from database.session import engine, SessionLocal
from models.base import Base
from models.entities import Department


DEFAULT_DEPARTMENTS = [
    "Agronomy",
    "Horticulture",
    "Plant Protection",
    "Veterinary Science",
    "Soil Science",
    "Home Science",
    "Agricultural Extension",
]


def create_tables() -> None:
    """Creates ORM-managed tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
    _ensure_oft_activity_columns()
    _seed_settings()


def _seed_settings() -> None:
    """Inserts office settings the first time, without overwriting staff changes."""
    from models.entities import AppSetting

    defaults = {
        "kvk_name": "Krishi Vigyan Kendra",
        "kvk_address": "",
        "backup_folder": "backups",
        "session_timeout_minutes": "30",
        "backup_overdue_days": "7",
        "last_import_invalid": "0",
    }
    session = SessionLocal()
    try:
        existing = {row.key for row in session.query(AppSetting.key).all()}
        for key, value in defaults.items():
            if key not in existing:
                session.add(AppSetting(key=key, value=value))
        session.commit()
    finally:
        session.close()


def _ensure_oft_activity_columns() -> None:
    """Adds newer activity columns to existing databases without destructive migrations."""
    statements = [
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS visitor_scientist VARCHAR(150)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS visitor_district VARCHAR(100)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS visitor_tehsil VARCHAR(100)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_title VARCHAR(255)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_batch_key VARCHAR(64)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_crop_variety VARCHAR(255)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_farmer_count INTEGER",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_technical_assessment TEXT",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_area VARCHAR(255)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_farmer_scientist VARCHAR(150)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_farmer_purpose VARCHAR(100)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_farmer_district VARCHAR(100)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_farmer_tehsil VARCHAR(100)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS oft_farmer_category VARCHAR(50)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_title VARCHAR(255)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_type VARCHAR(50)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_end_date DATE",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS clientele VARCHAR(10)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS thematic_area VARCHAR(255)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS venue VARCHAR(255)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS venue_is_offline BOOLEAN",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS venue_village VARCHAR(150)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS venue_taluka VARCHAR(150)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS venue_district VARCHAR(150)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_farmer_count INTEGER",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_farmer_category VARCHAR(50)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_farmer_scientist VARCHAR(150)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_farmer_purpose VARCHAR(100)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_farmer_district VARCHAR(100)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS training_farmer_tehsil VARCHAR(100)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS extension_venue VARCHAR(255)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS extension_location VARCHAR(255)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS extension_department VARCHAR(150)",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS extension_purpose TEXT",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS extension_farmer_count INTEGER",
        "ALTER TABLE activities ADD COLUMN IF NOT EXISTS other_extension_title VARCHAR(255)",
        "ALTER TABLE farmers ADD COLUMN IF NOT EXISTS farmer_code VARCHAR(20)",
        """
        UPDATE farmers
        SET farmer_code = 'KVK-F-' || LPAD(id::text, 6, '0')
        WHERE farmer_code IS NULL OR BTRIM(farmer_code) = ''
        """,
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_farmers_farmer_code ON farmers (farmer_code)",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'chk_activity_clientele'
            ) THEN
                ALTER TABLE activities
                    ADD CONSTRAINT chk_activity_clientele
                    CHECK (clientele IS NULL OR clientele IN ('PF', 'RY', 'EF')) NOT VALID;
            END IF;
        END $$;
        """,
        """
        UPDATE farmers
        SET farmer_name = 'N/A'
        WHERE id IN (
            SELECT f.id
            FROM farmers f
            JOIN activities a ON a.farmer_id = f.id
            WHERE a.module_type IN ('Extension Activities', 'Other Extension Activities')
              AND (
                  f.farmer_name LIKE 'Extension Activity - %'
                  OR f.farmer_name LIKE 'Other Extension Activity - %'
              )
              AND NOT EXISTS (
                  SELECT 1
                  FROM activities other_activity
                  WHERE other_activity.farmer_id = f.id
                    AND other_activity.module_type NOT IN ('Extension Activities', 'Other Extension Activities')
              )
        )
        """,
    ]
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def seed_departments() -> None:
    """Seeds department master data for first-time setup."""
    session = SessionLocal()
    try:
        existing = {name for (name,) in session.query(Department.name).all()}
        for dept_name in DEFAULT_DEPARTMENTS:
            if dept_name not in existing:
                session.add(Department(name=dept_name))
        session.commit()
    finally:
        session.close()


def test_connection() -> bool:
    """Quick health-check for PostgreSQL connectivity."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
