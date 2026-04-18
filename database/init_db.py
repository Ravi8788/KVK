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


def _ensure_oft_activity_columns() -> None:
    """Adds newer OFT columns to existing databases without destructive migrations."""
    statements = [
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
