from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.security import verify_password
from app.models.database import Resume, AIAnalysis
from app.services.quality_analyzer import get_quality_analyzer
from datetime import datetime

router = APIRouter(prefix="/api/v1/quality", tags=["quality-analysis"])

@router.post("/analyze/{resume_id}")
async def analyze_resume_quality(
    resume_id: str,
    target_role: Optional[str] = None,
    location: Optional[str] = "US",
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """
    Perform comprehensive quality analysis on a resume

    - **resume_id**: UUID of the resume to analyze
    - **target_role**: Optional target job role for tailored suggestions
    - **location**: Location for salary estimation (default: US)
    """
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if resume.status != 'completed':
        raise HTTPException(
            status_code=400,
            detail=f"Resume must be processed first. Current status: {resume.status}"
        )

    if not resume.structured_data:
        raise HTTPException(status_code=400, detail="No structured data available")

    analyzer = get_quality_analyzer()

    quality_analysis = analyzer.analyze_quality(resume.structured_data)
    salary_estimate = analyzer.estimate_salary_range(resume.structured_data, location)
    improvement_plan = analyzer.generate_improvement_plan(resume.structured_data, target_role)

    existing_analysis = db.query(AIAnalysis).filter(
        AIAnalysis.resume_id == uuid.UUID(resume_id)
    ).first()

    if existing_analysis:
        existing_analysis.quality_score = quality_analysis.get("quality_score", 0)
        existing_analysis.completeness_score = quality_analysis.get("completeness_score", 0)
        existing_analysis.industry_classifications = quality_analysis.get("industry_classifications", [])
        existing_analysis.career_level = quality_analysis.get("career_level", "Unknown")
        existing_analysis.salary_estimate = salary_estimate
        existing_analysis.suggestions = {
            "quality_analysis": quality_analysis,
            "improvement_plan": improvement_plan
        }
        existing_analysis.confidence_scores = {
            "ats_compatibility": quality_analysis.get("ats_compatibility_score", 0),
            "salary_confidence": salary_estimate.get("confidence", "low")
        }
        db.commit()
        db.refresh(existing_analysis)
        analysis = existing_analysis
    else:
        analysis = AIAnalysis(
            resume_id=uuid.UUID(resume_id),
            quality_score=quality_analysis.get("quality_score", 0),
            completeness_score=quality_analysis.get("completeness_score", 0),
            industry_classifications=quality_analysis.get("industry_classifications", []),
            career_level=quality_analysis.get("career_level", "Unknown"),
            salary_estimate=salary_estimate,
            suggestions={
                "quality_analysis": quality_analysis,
                "improvement_plan": improvement_plan
            },
            confidence_scores={
                "ats_compatibility": quality_analysis.get("ats_compatibility_score", 0),
                "salary_confidence": salary_estimate.get("confidence", "low")
            },
            created_at=datetime.utcnow()
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

    return {
        "id": str(analysis.id),
        "resume_id": resume_id,
        "quality_score": analysis.quality_score,
        "completeness_score": analysis.completeness_score,
        "career_level": analysis.career_level,
        "industry_classifications": analysis.industry_classifications,
        "salary_estimate": analysis.salary_estimate,
        "quality_analysis": quality_analysis,
        "improvement_plan": improvement_plan,
        "confidence_scores": analysis.confidence_scores,
        "created_at": analysis.created_at
    }

@router.get("/{resume_id}")
async def get_quality_analysis(
    resume_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """Get existing quality analysis for a resume"""
    analysis = db.query(AIAnalysis).filter(
        AIAnalysis.resume_id == uuid.UUID(resume_id)
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="No quality analysis found. Run analysis first."
        )

    return {
        "id": str(analysis.id),
        "resume_id": resume_id,
        "quality_score": analysis.quality_score,
        "completeness_score": analysis.completeness_score,
        "career_level": analysis.career_level,
        "industry_classifications": analysis.industry_classifications,
        "salary_estimate": analysis.salary_estimate,
        "suggestions": analysis.suggestions,
        "confidence_scores": analysis.confidence_scores,
        "created_at": analysis.created_at
    }

@router.delete("/{resume_id}")
async def delete_quality_analysis(
    resume_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """Delete quality analysis for a resume"""
    analysis = db.query(AIAnalysis).filter(
        AIAnalysis.resume_id == uuid.UUID(resume_id)
    ).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    db.delete(analysis)
    db.commit()

    return {
        "message": "Quality analysis deleted successfully",
        "resume_id": resume_id
    }

