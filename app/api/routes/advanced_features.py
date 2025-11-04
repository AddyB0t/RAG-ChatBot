"""
Advanced Features API Routes
Includes bias detection, anonymization, competitive analysis, and candidate ranking
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.core.security import verify_password
from app.models.database import Resume, ResumeJobMatch
from app.services.bias_detector import get_bias_detector
from app.services.anonymizer import get_anonymizer
from app.services.competitive_analyzer import get_competitive_analyzer
from app.services.candidate_ranker import get_candidate_ranker
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/advanced", tags=["advanced-features"])

class BiasDetectionResponse(BaseModel):
    resume_id: str
    has_bias: bool
    bias_score: float
    overall_risk: str
    biases_detected: List[dict]
    total_bias_indicators: int
    categories_affected: List[str]
    recommendations: List[str]
    analyzed_at: str

class AnonymizationRequest(BaseModel):
    resume_id: str
    options: Optional[dict] = None

class AnonymizationResponse(BaseModel):
    resume_id: str
    anonymized_data: dict
    anonymization_report: dict
    success: bool

class CompetitiveAnalysisRequest(BaseModel):
    resume_id: str
    job_description: str
    job_title: str

class CompetitiveAnalysisResponse(BaseModel):
    resume_id: str
    competitive_score: float
    market_position: str
    industry_benchmark: str
    experience_analysis: dict
    skills_analysis: dict
    education_analysis: dict
    strengths: List[str]
    weaknesses: List[str]
    competitive_advantages: List[dict]
    improvement_priorities: List[dict]
    market_insights: List[str]

class CandidateRankingRequest(BaseModel):
    resume_ids: List[str]
    job_description: str
    job_title: str
    weights: Optional[dict] = None

class CandidateRankingResponse(BaseModel):
    total_candidates: int
    ranked_candidates: List[dict]
    tier_distribution: dict
    statistics: dict
    weights_used: dict
    ranking_criteria: List[str]

@router.post("/bias-detection/{resume_id}", response_model=BiasDetectionResponse)
async def detect_bias(
    resume_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """
    Detect potential biases in resume content

    Analyzes resume for gender, age, cultural, disability, and other biases
    Returns bias score, risk level, and recommendations
    """
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume.structured_data:
        raise HTTPException(
            status_code=400,
            detail="Resume not yet processed. Please wait for processing to complete."
        )

    bias_detector = get_bias_detector()
    bias_result = bias_detector.detect_bias_in_resume(resume.structured_data)

    return BiasDetectionResponse(
        resume_id=resume_id,
        **bias_result
    )

@router.post("/anonymize", response_model=AnonymizationResponse)
async def anonymize_resume(
    request: AnonymizationRequest,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """
    Anonymize resume by removing PII

    Options:
    - remove_name: Remove candidate name (default: True)
    - remove_contact: Remove contact information (default: True)
    - remove_address: Remove address (default: True)
    - remove_age_dob: Remove age/DOB (default: True)
    - remove_gender: Remove gender indicators (default: True)
    - mask_education_dates: Mask education dates (default: True)
    - mask_work_dates: Mask work dates (default: False)
    - remove_company_names: Remove company names (default: False)
    - remove_school_names: Remove school names (default: False)
    """
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(request.resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume.structured_data:
        raise HTTPException(
            status_code=400,
            detail="Resume not yet processed. Please wait for processing to complete."
        )

    anonymizer = get_anonymizer()
    anonymized_data = anonymizer.anonymize_resume(
        resume.structured_data,
        options=request.options
    )

    anonymization_report = anonymizer.get_anonymization_report(
        resume.structured_data,
        anonymized_data
    )

    return AnonymizationResponse(
        resume_id=request.resume_id,
        anonymized_data=anonymized_data,
        anonymization_report=anonymization_report,
        success=True
    )

@router.post("/competitive-analysis", response_model=CompetitiveAnalysisResponse)
async def analyze_competitiveness(
    request: CompetitiveAnalysisRequest,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """
    Analyze candidate competitiveness in the market

    Compares candidate against industry benchmarks
    Provides market position, strengths, weaknesses, and improvement priorities
    """
    resume = db.query(Resume).filter(Resume.id == uuid.UUID(request.resume_id)).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if not resume.structured_data:
        raise HTTPException(
            status_code=400,
            detail="Resume not yet processed. Please wait for processing to complete."
        )

    from app.services.job_matcher.matcher_manager import get_job_matcher
    matcher = get_job_matcher()
    match_result = matcher.match_resume_to_job(
        resume_data=resume.structured_data,
        job_description=request.job_description,
        job_title=request.job_title,
        company_name=None
    )

    competitive_analyzer = get_competitive_analyzer()
    competitive_result = competitive_analyzer.analyze_competitiveness(
        resume_data=resume.structured_data,
        job_requirements=match_result.get("job_requirements", {}),
        match_score=match_result["overall_score"]
    )

    return CompetitiveAnalysisResponse(
        resume_id=request.resume_id,
        competitive_score=competitive_result['competitive_score'],
        market_position=competitive_result['market_position']['position'],
        industry_benchmark=competitive_result['industry_benchmark'],
        experience_analysis=competitive_result['experience_analysis'],
        skills_analysis=competitive_result['skills_analysis'],
        education_analysis=competitive_result['education_analysis'],
        strengths=competitive_result['strengths'],
        weaknesses=competitive_result['weaknesses'],
        competitive_advantages=competitive_result['competitive_advantages'],
        improvement_priorities=competitive_result['improvement_priorities'],
        market_insights=competitive_result['market_insights']
    )

@router.post("/rank-candidates", response_model=CandidateRankingResponse)
async def rank_candidates(
    request: CandidateRankingRequest,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """
    Rank multiple candidates for a job position

    Uses multi-criteria analysis to rank candidates
    Provides detailed scoring, tier distribution, and statistics

    Custom weights (optional):
    - skills_match: 0.30 (default)
    - experience_match: 0.25 (default)
    - education_match: 0.15 (default)
    - cultural_fit: 0.10 (default)
    - career_trajectory: 0.10 (default)
    - certifications: 0.05 (default)
    - availability: 0.05 (default)
    """
    candidates = []

    for resume_id in request.resume_ids:
        try:
            resume = db.query(Resume).filter(Resume.id == uuid.UUID(resume_id)).first()

            if not resume or not resume.structured_data:
                continue

            from app.services.job_matcher.matcher_manager import get_job_matcher
            matcher = get_job_matcher()
            match_result = matcher.match_resume_to_job(
                resume_data=resume.structured_data,
                job_description=request.job_description,
                job_title=request.job_title,
                company_name=None
            )

            candidates.append({
                'resume_id': resume_id,
                'resume_data': resume.structured_data,
                'match_data': match_result,
                'availability': 'unknown'
            })

        except Exception as e:
            continue

    if not candidates:
        raise HTTPException(
            status_code=400,
            detail="No valid candidates found with processed resumes"
        )

    ranker = get_candidate_ranker()

    from app.services.job_matcher.job_parser import JobDescriptionParser
    job_parser = JobDescriptionParser()
    job_requirements = job_parser.parse_job_description(
        request.job_description,
        request.job_title
    )

    ranking_result = ranker.rank_candidates(
        candidates=candidates,
        job_requirements=job_requirements,
        weights=request.weights
    )

    return CandidateRankingResponse(**ranking_result)

@router.get("/bias-detection/job-description", response_model=dict)
async def detect_job_description_bias(
    job_description: str,
    authenticated: bool = Depends(verify_password)
):
    """
    Detect potential biases in job description

    Analyzes job description for biased language
    Provides inclusive language score and recommendations
    """
    bias_detector = get_bias_detector()
    bias_result = bias_detector.detect_bias_in_job_description(job_description)

    return bias_result

@router.post("/candidate-comparison")
async def compare_candidates(
    candidate1_id: str,
    candidate2_id: str,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_password)
):
    """
    Direct comparison between two candidates

    Provides side-by-side comparison of scores and strengths
    Works with both resumes (with or without job matches)
    """
    resume1 = db.query(Resume).filter(Resume.id == uuid.UUID(candidate1_id)).first()
    resume2 = db.query(Resume).filter(Resume.id == uuid.UUID(candidate2_id)).first()

    if not resume1 or not resume2:
        raise HTTPException(
            status_code=404,
            detail="One or both candidates not found"
        )

    job_match1 = db.query(ResumeJobMatch).filter(
        ResumeJobMatch.resume_id == uuid.UUID(candidate1_id)
    ).first()

    job_match2 = db.query(ResumeJobMatch).filter(
        ResumeJobMatch.resume_id == uuid.UUID(candidate2_id)
    ).first()

    ranker = get_candidate_ranker()

    candidate1_data = {
        'resume_id': candidate1_id,
        'final_score': job_match1.overall_score if job_match1 else 0.0,
        'category_scores': job_match1.category_scores if job_match1 else {},
        'structured_data': resume1.structured_data or {}
    }

    candidate2_data = {
        'resume_id': candidate2_id,
        'final_score': job_match2.overall_score if job_match2 else 0.0,
        'category_scores': job_match2.category_scores if job_match2 else {},
        'structured_data': resume2.structured_data or {}
    }

    comparison = ranker.compare_candidates(candidate1_data, candidate2_data)

    return comparison
