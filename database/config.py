import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    """Builds PostgreSQL SQLAlchemy URL from environment variables."""
    direct_url = os.getenv("DATABASE_URL", "").strip()
    if direct_url:
        return direct_url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "kvk_db")
    raw_user = os.getenv("DB_USER", "postgres")
    raw_password = os.getenv("DB_PASSWORD", "")
    user = quote_plus(raw_user)
    password = quote_plus(raw_password)

    app_env = os.getenv("APP_ENV", "development").strip().lower()
    if app_env == "production":
        if raw_password in {"", "postgres"}:
            raise ValueError("DB_PASSWORD must be set to a strong value in production.")

    sslmode = os.getenv("DB_SSLMODE", "").strip().lower()
    if not sslmode:
        sslmode = "disable" if host in {"localhost", "127.0.0.1"} else "require"

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}?sslmode={sslmode}"
