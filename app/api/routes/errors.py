from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.core.security import verify_password
from app.models.database import ResumeParserErrorLog

router = APIRouter(prefix="/api/v1/error-logs", tags=["error-logs"])

@router.get("")
async def get_all_error_logs(
    limit: int = 50,
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    query = db.query(ResumeParserErrorLog)

    if severity:
        query = query.filter(ResumeParserErrorLog.severity == severity)

    if is_resolved is not None:
        query = query.filter(ResumeParserErrorLog.is_resolved == is_resolved)

    error_logs = query.order_by(
        ResumeParserErrorLog.created_at.desc()
    ).limit(limit).all()

    return {
        "error_logs": [
            {
                "id": str(log.id),
                "resume_id": str(log.resume_id) if log.resume_id else None,
                "error_type": log.error_type,
                "error_message": log.error_message,
                "extractor_name": log.extractor_name,
                "severity": log.severity,
                "is_resolved": log.is_resolved,
                "created_at": log.created_at,
                "resolved_at": log.resolved_at
            }
            for log in error_logs
        ],
        "count": len(error_logs),
        "filters": {"severity": severity, "is_resolved": is_resolved}
    }

@router.get("/stats")
async def get_error_log_stats(
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    total_errors = db.query(ResumeParserErrorLog).count()
    unresolved_errors = db.query(ResumeParserErrorLog).filter(
        ResumeParserErrorLog.is_resolved == False
    ).count()
    critical_errors = db.query(ResumeParserErrorLog).filter(
        ResumeParserErrorLog.severity == 'critical',
        ResumeParserErrorLog.is_resolved == False
    ).count()

    error_types = db.query(
        ResumeParserErrorLog.error_type,
        db.func.count(ResumeParserErrorLog.id)
    ).group_by(ResumeParserErrorLog.error_type).all()

    return {
        "total_errors": total_errors,
        "unresolved_errors": unresolved_errors,
        "critical_errors": critical_errors,
        "error_types": {error_type: count for error_type, count in error_types}
    }

@router.get("/resumes/{resume_id}")
async def get_resume_error_logs(
    resume_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    error_logs = db.query(ResumeParserErrorLog).filter(
        ResumeParserErrorLog.resume_id == uuid.UUID(resume_id)
    ).order_by(ResumeParserErrorLog.created_at.desc()).all()

    return {
        "resume_id": resume_id,
        "error_logs": [
            {
                "id": str(log.id),
                "error_type": log.error_type,
                "error_message": log.error_message,
                "stack_trace": log.stack_trace,
                "extractor_name": log.extractor_name,
                "input_data": log.input_data,
                "context": log.context,
                "severity": log.severity,
                "is_resolved": log.is_resolved,
                "created_at": log.created_at,
                "resolved_at": log.resolved_at
            }
            for log in error_logs
        ],
        "count": len(error_logs)
    }

@router.put("/{error_log_id}/resolve")
async def resolve_error_log(
    error_log_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    error_log = db.query(ResumeParserErrorLog).filter(
        ResumeParserErrorLog.id == uuid.UUID(error_log_id)
    ).first()

    if not error_log:
        raise HTTPException(status_code=404, detail="Error log not found")

    error_log.is_resolved = True
    error_log.resolved_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Error log marked as resolved",
        "id": error_log_id,
        "resolved_at": error_log.resolved_at
    }

@router.delete("/cleanup")
async def cleanup_old_error_logs(
    days_old: int = 30,
    resolved_only: bool = True,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    query = db.query(ResumeParserErrorLog).filter(ResumeParserErrorLog.created_at < cutoff_date)

    if resolved_only:
        query = query.filter(ResumeParserErrorLog.is_resolved == True)

    deleted_count = query.delete()
    db.commit()

    return {
        "message": f"Deleted {deleted_count} old error logs",
        "deleted_count": deleted_count,
        "days_old": days_old,
        "resolved_only": resolved_only
    }

