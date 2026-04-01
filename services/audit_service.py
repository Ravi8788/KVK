from typing import Optional
import logging

from sqlalchemy.exc import IntegrityError
from database.session import SessionLocal
from models.entities import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Records user actions for audit and traceability."""

    @staticmethod
    def log_action(
        user_id: Optional[int],
        action: str,
        module_type: Optional[str] = None,
        record_id: Optional[int] = None,
        details: Optional[str] = None,
    ) -> None:
        session = SessionLocal()
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                module_type=module_type,
                record_id=record_id,
                details=details,
            )
            session.add(log)
            session.commit()
        except IntegrityError as e:
            # If duplicate key or constraint error, log warning but don't crash the operation
            session.rollback()
            logger.warning(f"Audit log insertion failed (will retry on next sequence sync): {action} - {str(e)}")
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error in audit logging: {str(e)}")
        finally:
            session.close()
