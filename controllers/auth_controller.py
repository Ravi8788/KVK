import os
import time
from typing import Optional

from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from database.session import SessionLocal
from models.entities import User


class AuthController:
    """Handles login validation and first-run admin provisioning."""

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_SECONDS = 300
    _failed_attempts = {}

    @staticmethod
    def ensure_default_admin() -> None:
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "admin123")

        session = SessionLocal()
        try:
            admin = session.query(User).filter(User.username == username).first()
            if admin is None:
                session.add(
                    User(
                        username=username,
                        full_name="System Administrator",
                        password_hash=pbkdf2_sha256.hash(password),
                        role="admin",
                        is_active=True,
                    )
                )
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def login(username: str, password: str) -> Optional[User]:
        username = username.strip()
        if not username or len(username) > 80:
            return None

        # Simple in-process lockout to slow repeated password guessing attempts.
        lock_until = AuthController._failed_attempts.get(username, {}).get("lock_until", 0)
        if lock_until and lock_until > time.time():
            return None

        session = SessionLocal()
        try:
            user = session.query(User).filter(User.username == username, User.is_active.is_(True)).first()
            if not user:
                AuthController._register_failed_attempt(username)
                return None
            if not pbkdf2_sha256.verify(password, user.password_hash):
                AuthController._register_failed_attempt(username)
                return None

            AuthController._failed_attempts.pop(username, None)
            session.expunge(user)
            return user
        finally:
            session.close()

    @staticmethod
    def _register_failed_attempt(username: str) -> None:
        now = time.time()
        state = AuthController._failed_attempts.get(username, {"count": 0, "lock_until": 0})
        state["count"] += 1
        if state["count"] >= AuthController.MAX_FAILED_ATTEMPTS:
            state["lock_until"] = now + AuthController.LOCKOUT_SECONDS
            state["count"] = 0
        AuthController._failed_attempts[username] = state
