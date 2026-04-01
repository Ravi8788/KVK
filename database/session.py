from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import get_database_url

# Pool settings are tuned for a local desktop app with occasional heavy report reads.
engine = create_engine(
    get_database_url(),
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,
    connect_args={
        "connect_timeout": 10,
        "application_name": "KVKSystem",
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Yields a transactional SQLAlchemy session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
