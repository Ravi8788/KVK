import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Builds PostgreSQL SQLAlchemy URL from environment variables."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "kvk_db")
    user = quote_plus(os.getenv("DB_USER", "postgres"))
    password = quote_plus(os.getenv("DB_PASSWORD", "postgres"))
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
