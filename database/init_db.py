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
