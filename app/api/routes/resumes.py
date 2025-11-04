from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pathlib import Path
import os
import shutil
import uuid

from app.core.database import get_db, SessionLocal
from app.core.security import verify_password
from app.models.database import Resume
from app.schemas.resume import ResumeUploadResponse, ResumeResponse, ResumeStatusResponse
from app.services.resume_parser.parser_manager import get_resume_parser
from app.services.malware_scanner import get_malware_scanner
from app.core.config import settings

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)

async def process_resume_background_async(resume_id: str, file_path: str):
    """Background task to process resume after upload"""
    db = SessionLocal()
    try:
        from app.services.document_loader import load_single_document

        resume = db.query(Resume).filter(Resume.id == uuid.UUID(resume_id)).first()
        if not resume:
            return

        resume.status = 'processing'
        db.commit()

        documents = load_single_document(file_path)
        if documents:
            raw_text = " ".join([doc.page_content for doc in documents])
            resume.raw_text = raw_text

            parser = get_resume_parser()
            structured_data = await parser.parse_resume_async(raw_text, resume_id=resume_id, db=db)

            resume.structured_data = structured_data
            resume.status = 'completed'
            resume.processed_at = datetime.utcnow()
        else:
            resume.status = 'failed'

        db.commit()

    except Exception as e:
        resume.status = 'failed'
        db.commit()
        from app.services.resume_parser.error_logger import ResumeParserErrorLogger
        ResumeParserErrorLogger.log_error(
            db, e, "resume_parsing_failed", "BackgroundTask",
            resume_id, {"file_path": file_path}, None, "critical"
        )
    finally:
        db.close()

def process_resume_background(resume_id: str, file_path: str):
    """Wrapper to run async function in background"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(process_resume_background_async(resume_id, file_path))

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    allowed_extensions = {'.pdf', '.docx', '.doc', '.txt'}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    file_content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    file_size = os.path.getsize(file_path)

    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
        )

    scanner = get_malware_scanner()
    scan_result = scanner.scan_file(file_path, file.filename, settings.MAX_FILE_SIZE_MB)

    if not scan_result['is_safe']:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File rejected by security scan",
                "threats": scan_result['threats_found'],
                "scan_summary": scan_result['scan_summary']
            }
        )

    parser = get_resume_parser()
    file_hash = parser.generate_resume_hash(file_content, file.filename)

    existing_resume = db.query(Resume).filter(Resume.file_hash == file_hash).first()

    if existing_resume:
        os.remove(file_path)

        return ResumeUploadResponse(
            id=str(existing_resume.id),
            message=f"Resume '{file.filename}' already exists. Returning existing record.",
            filename=existing_resume.file_name,
            status=existing_resume.status,
            uploaded_at=existing_resume.uploaded_at
        )

    resume = Resume(
        file_name=file.filename,
        file_path=file_path,
        file_hash=file_hash,
        file_size=file_size,
        file_type=file_extension[1:],
        status='pending',
        uploaded_at=datetime.utcnow()
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    background_tasks.add_task(process_resume_background, str(resume.id), file_path)

    return ResumeUploadResponse(
        id=str(resume.id),
        message=f"Resume '{file.filename}' uploaded successfully. Processing in background.",
        filename=file.filename,
        status="pending",
        uploaded_at=resume.uploaded_at
    )

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return ResumeResponse(
        id=str(resume.id),
        file_name=resume.file_name,
        file_path=resume.file_path,
        file_size=resume.file_size,
        file_type=resume.file_type,
        status=resume.status,
        uploaded_at=resume.uploaded_at,
        processed_at=resume.processed_at,
        structured_data=resume.structured_data,
        raw_text=resume.raw_text
    )

@router.put("/{resume_id}")
async def update_resume(
    resume_id: str,
    updated_data: dict,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if "structured_data" in updated_data:
        resume.structured_data = updated_data["structured_data"]

    resume.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume updated successfully",
        "id": str(resume.id),
        "updated_at": resume.updated_at
    }

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    file_path = resume.file_path
    filename = resume.file_name

    file_deleted = False
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            file_deleted = True
        except Exception:
            pass

    db.delete(resume)
    db.commit()

    return {
        "message": f"Resume '{filename}' deleted successfully",
        "id": resume_id,
        "filename": filename,
        "file_deleted": file_deleted
    }

@router.get("/{resume_id}/status", response_model=ResumeStatusResponse)
async def get_resume_status(
    resume_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    status_messages = {
        'pending': 'Resume uploaded, processing will start shortly',
        'processing': 'Resume is currently being processed',
        'completed': 'Resume processing completed successfully',
        'failed': 'Resume processing failed'
    }

    return ResumeStatusResponse(
        id=str(resume.id),
        status=resume.status,
        message=status_messages.get(resume.status, "Unknown status"),
        processed_at=resume.processed_at
    )

@router.get("/")
async def list_resumes(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """List all uploaded resumes with pagination"""
    resumes = db.query(Resume).offset(skip).limit(limit).all()

    return {
        "count": len(resumes),
        "resumes": [
            {
                "id": str(resume.id),
                "file_name": resume.file_name,
                "status": resume.status,
                "uploaded_at": resume.uploaded_at,
                "processed_at": resume.processed_at
            }
            for resume in resumes
        ]
    }

