from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import verify_password
from app.models.database import Resume, ResumeJobMatch
from app.schemas.job_match import JobMatchRequest, JobMatchResponse, JobMatchDetailResponse
from app.services.job_matcher.matcher_manager import get_job_matcher

router = APIRouter(prefix="/api/v1/jobs", tags=["job-matching"])

@router.post("/match", response_model=JobMatchResponse)
async def match_resume_to_job(
    match_request: JobMatchRequest,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(match_request.resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume.structured_data:
        raise HTTPException(
            status_code=400,
            detail="Resume not yet processed. Please wait for processing to complete."
        )

    matcher = get_job_matcher()
    match_result = matcher.match_resume_to_job(
        resume_data=resume.structured_data,
        job_description=match_request.job_description,
        job_title=match_request.job_title,
        company_name=match_request.company_name
    )

    job_match = ResumeJobMatch(
        resume_id=resume.id,
        job_title=match_request.job_title,
        company_name=match_request.company_name,
        job_description=match_request.job_description,
        job_requirements=match_result.get("job_requirements"),
        overall_score=int(match_result["overall_score"]),
        confidence_score=match_result["confidence_score"] / 100,
        recommendation=match_result["recommendation"],
        category_scores=match_result["category_scores"],
        strength_areas=match_result["strength_areas"],
        gap_analysis=match_result["gap_analysis"],
        processing_metadata={
            "skill_analysis": match_result["skill_analysis"],
            "experience_analysis": match_result["experience_analysis"],
            "education_match": match_result["education_match"]
        },
        matched_at=datetime.utcnow()
    )

    db.add(job_match)
    db.commit()
    db.refresh(job_match)

    return JobMatchResponse(
        id=str(job_match.id),
        resume_id=str(job_match.resume_id),
        job_title=job_match.job_title,
        company_name=job_match.company_name,
        overall_score=job_match.overall_score,
        confidence_score=float(job_match.confidence_score),
        recommendation=job_match.recommendation,
        category_scores=job_match.category_scores,
        matched_at=job_match.matched_at
    )

@router.get("/matches/{match_id}", response_model=JobMatchDetailResponse)
async def get_match_details(
    match_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    job_match = db.query(ResumeJobMatch).filter(ResumeJobMatch.id == uuid.UUID(match_id)).first()

    if not job_match:
        raise HTTPException(status_code=404, detail="Job match not found")

    metadata = job_match.processing_metadata or {}

    return JobMatchDetailResponse(
        id=str(job_match.id),
        resume_id=str(job_match.resume_id),
        job_title=job_match.job_title,
        company_name=job_match.company_name,
        overall_score=job_match.overall_score,
        confidence_score=float(job_match.confidence_score),
        recommendation=job_match.recommendation,
        category_scores=job_match.category_scores or {},
        skill_analysis=metadata.get("skill_analysis", {}),
        experience_analysis=metadata.get("experience_analysis", {}),
        education_match=metadata.get("education_match", {}),
        gap_analysis=job_match.gap_analysis or {},
        strength_areas=job_match.strength_areas or [],
        job_requirements=job_match.job_requirements or {},
        matched_at=job_match.matched_at
    )

@router.get("/resumes/{resume_id}/matches", response_model=List[JobMatchResponse])
async def get_resume_matches(
    resume_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    matches = db.query(ResumeJobMatch).filter(
        ResumeJobMatch.resume_id == uuid.UUID(resume_id)
    ).order_by(ResumeJobMatch.matched_at.desc()).all()

    return [
        JobMatchResponse(
            id=str(match.id),
            resume_id=str(match.resume_id),
            job_title=match.job_title,
            company_name=match.company_name,
            overall_score=match.overall_score,
            confidence_score=float(match.confidence_score),
            recommendation=match.recommendation,
            category_scores=match.category_scores or {},
            matched_at=match.matched_at
        )
        for match in matches
    ]

@router.delete("/matches/{match_id}")
async def delete_job_match(
    match_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    job_match = db.query(ResumeJobMatch).filter(ResumeJobMatch.id == uuid.UUID(match_id)).first()

    if not job_match:
        raise HTTPException(status_code=404, detail="Job match not found")

    db.delete(job_match)
    db.commit()

    return {
        "message": "Job match deleted successfully",
        "id": match_id
    }

