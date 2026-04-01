from typing import List

from passlib.hash import pbkdf2_sha256

from database.session import SessionLocal
from models.entities import User
from services.audit_service import AuditService


class UserService:
    """Admin-only operations for staff and admin user accounts."""

    @staticmethod
    def create_user(
        username: str,
        full_name: str,
        password: str,
        role: str,
        created_by: int,
    ) -> int:
        session = SessionLocal()
        try:
            existing = session.query(User).filter(User.username == username.strip()).first()
            if existing:
                raise ValueError("Username already exists")

            user = User(
                username=username.strip(),
                full_name=full_name.strip(),
                password_hash=pbkdf2_sha256.hash(password),
                role=role,
                is_active=True,
            )
            session.add(user)
            session.commit()

            AuditService.log_action(
                user_id=created_by,
                action="create_user",
                module_type="User Management",
                record_id=user.id,
                details=f"Created user: {username}",
            )
            return user.id
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def list_users() -> List[User]:
        session = SessionLocal()
        try:
            users = session.query(User).order_by(User.created_at.desc()).all()
            for user in users:
                session.expunge(user)
            return users
        finally:
            session.close()

    @staticmethod
    def set_active_status(user_id: int, is_active: bool, changed_by: int) -> None:
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user is None:
                raise ValueError("User not found")
            user.is_active = is_active
            session.commit()

            AuditService.log_action(
                user_id=changed_by,
                action="activate_user" if is_active else "deactivate_user",
                module_type="User Management",
                record_id=user_id,
                details="Updated user status",
            )
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
