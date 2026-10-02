import os
import time
from typing import Optional

from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from database.session import SessionLocal
from models.entities import User
from services.audit_service import AuditService


class AuthController:
    """Handles login validation and first-run admin provisioning."""

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_SECONDS = 300
    _failed_attempts = {}

    @staticmethod
    def ensure_default_admin() -> None:
        username = os.getenv("ADMIN_USERNAME", "admin")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        app_env = os.getenv("APP_ENV", "development").strip().lower()

        if app_env == "production" and password in {"", "admin123", "password", "admin"}:
            raise ValueError("Set a strong ADMIN_PASSWORD in production before first launch.")

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
                AuditService.log_action(None, "login_failed", "Authentication", None, f"Unknown or inactive user {username}")
                return None
            if not pbkdf2_sha256.verify(password, user.password_hash):
                AuthController._register_failed_attempt(username)
                AuditService.log_action(user.id, "login_failed", "Authentication", user.id, f"Wrong password for {username}")
                return None

            AuthController._failed_attempts.pop(username, None)
            user_id = user.id
            session.expunge(user)
            AuditService.log_action(user_id, "login", "Authentication", user_id, f"Login succeeded for {username}")
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

    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> None:
        if len(new_password or "") < 8:
            raise ValueError("New password must be at least 8 characters.")
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
            if user is None or not pbkdf2_sha256.verify(current_password, user.password_hash):
                raise ValueError("Current password is not correct.")
            user.password_hash = pbkdf2_sha256.hash(new_password)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        AuditService.log_action(user_id, "change_password", "Settings", user_id, "Password changed")
