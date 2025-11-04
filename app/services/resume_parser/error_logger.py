import traceback
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class ResumeParserErrorLogger:

    @staticmethod
    def log_error(
        db: Session,
        error: Exception,
        error_type: str,
        extractor_name: str,
        resume_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        severity: str = 'error'
    ):
        try:
            from app.models.database import ResumeParserErrorLog
            import uuid

            error_log = ResumeParserErrorLog(
                resume_id=uuid.UUID(resume_id) if resume_id else None,
                error_type=error_type,
                error_message=str(error),
                stack_trace=traceback.format_exc(),
                extractor_name=extractor_name,
                input_data=input_data,
                context=context,
                severity=severity,
                is_resolved=False,
                created_at=datetime.utcnow()
            )

            db.add(error_log)
            db.commit()

            logger.error(
                f"Resume parser error logged: {error_type} in {extractor_name} - {str(error)}"
            )

        except Exception as log_error:
            logger.error(f"Failed to log resume parser error: {log_error}")
            db.rollback()

    @staticmethod
    def log_warning(
        db: Session,
        message: str,
        extractor_name: str,
        resume_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        try:
            from app.models.database import ResumeParserErrorLog
            import uuid

            error_log = ResumeParserErrorLog(
                resume_id=uuid.UUID(resume_id) if resume_id else None,
                error_type='warning',
                error_message=message,
                stack_trace=None,
                extractor_name=extractor_name,
                input_data=None,
                context=context,
                severity='warning',
                is_resolved=False,
                created_at=datetime.utcnow()
            )

            db.add(error_log)
            db.commit()

            logger.warning(f"Resume parser warning: {message} in {extractor_name}")

        except Exception as log_error:
            logger.warning(f"Failed to log warning: {log_error}")
            db.rollback()

    @staticmethod
    def mark_resolved(db: Session, error_log_id: str):
        try:
            from app.models.database import ResumeParserErrorLog
            import uuid

            error_log = db.query(ResumeParserErrorLog).filter(
                ResumeParserErrorLog.id == uuid.UUID(error_log_id)
            ).first()

            if error_log:
                error_log.is_resolved = True
                error_log.resolved_at = datetime.utcnow()
                db.commit()

        except Exception as e:
            logger.error(f"Failed to mark error as resolved: {e}")
            db.rollback()

_error_logger_instance = None

def get_error_logger():
    global _error_logger_instance
    if _error_logger_instance is None:
        _error_logger_instance = ResumeParserErrorLogger()
    return _error_logger_instance

