from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class JobMatchRequest(BaseModel):
    resume_id: str
    job_title: str
    job_description: str
    company_name: Optional[str] = None

class JobMatchResponse(BaseModel):
    id: str
    resume_id: str
    job_title: str
    company_name: Optional[str]
    overall_score: float
    confidence_score: float
    recommendation: str
    category_scores: Dict[str, float]
    matched_at: datetime

class JobMatchDetailResponse(BaseModel):
    id: str
    resume_id: str
    job_title: str
    company_name: Optional[str]
    overall_score: float
    confidence_score: float
    recommendation: str
    category_scores: Dict[str, Any]
    skill_analysis: Dict[str, Any]
    experience_analysis: Dict[str, Any]
    education_match: Dict[str, Any]
    gap_analysis: Dict[str, Any]
    strength_areas: list
    job_requirements: Dict[str, Any]
    matched_at: datetime

