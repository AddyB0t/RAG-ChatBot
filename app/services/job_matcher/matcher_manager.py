from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from .job_parser import JobDescriptionParser
from .skill_matcher import SkillMatcher
from .experience_matcher import ExperienceMatcher
from .match_scorer import MatchScorer

logger = logging.getLogger(__name__)

class JobMatcherManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.job_parser = JobDescriptionParser()
        self.skill_matcher = SkillMatcher()
        self.experience_matcher = ExperienceMatcher()
        self.match_scorer = MatchScorer()

        self._initialized = True
        logger.info("Job Matcher Manager initialized")

    def match_resume_to_job(
        self,
        resume_data: Dict[str, Any],
        job_description: str,
        job_title: str,
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        logger.info(f"Starting job matching for: {job_title}")

        job_requirements = self.job_parser.parse_job_description(job_description, job_title)

        candidate_skills = resume_data.get("skills", {})
        skill_analysis = self.skill_matcher.match_skills(
            candidate_skills,
            job_requirements.get("required_skills", []),
            job_requirements.get("preferred_skills", [])
        )

        candidate_experience = resume_data.get("experience", [])
        experience_analysis = self.experience_matcher.match_experience(
            candidate_experience,
            job_requirements
        )

        education_match = self._match_education(
            resume_data.get("education", []),
            job_requirements.get("education_required", "")
        )

        scoring = self.match_scorer.calculate_overall_score(
            skill_analysis,
            experience_analysis,
            education_match
        )

        gap_analysis = self.match_scorer.generate_gap_analysis(
            resume_data,
            job_requirements,
            skill_analysis,
            experience_analysis
        )

        strength_areas = self._identify_strengths(
            skill_analysis,
            experience_analysis,
            education_match
        )

        return {
            "job_title": job_title,
            "company_name": company_name,
            "overall_score": scoring["overall_score"],
            "confidence_score": scoring["confidence_score"],
            "recommendation": scoring["recommendation"],
            "category_scores": scoring["category_scores"],
            "skill_analysis": skill_analysis,
            "experience_analysis": experience_analysis,
            "education_match": education_match,
            "gap_analysis": gap_analysis,
            "strength_areas": strength_areas,
            "job_requirements": job_requirements,
            "matched_at": datetime.utcnow().isoformat()
        }

    def _match_education(
        self,
        candidate_education: list,
        required_education: str
    ) -> Dict[str, Any]:
        if not required_education or not candidate_education:
            return {"score": 50, "meets_requirement": False, "details": "No education data"}

        education_levels = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "mba": 4,
            "phd": 5,
            "doctorate": 5
        }

        required_level = 0
        for level, value in education_levels.items():
            if level in required_education.lower():
                required_level = max(required_level, value)

        candidate_level = 0
        for edu in candidate_education:
            degree = (edu.get("degree", "") or "").lower()
            for level, value in education_levels.items():
                if level in degree:
                    candidate_level = max(candidate_level, value)

        if candidate_level >= required_level:
            score = 100
            meets = True
        elif candidate_level == required_level - 1:
            score = 75
            meets = False
        elif candidate_level > 0:
            score = 50
            meets = False
        else:
            score = 25
            meets = False

        return {
            "score": score,
            "meets_requirement": meets,
            "candidate_level": candidate_level,
            "required_level": required_level,
            "details": f"Candidate has education level {candidate_level}, required {required_level}"
        }

    def _identify_strengths(
        self,
        skill_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any],
        education_match: Dict[str, Any]
    ) -> list:
        strengths = []

        if skill_analysis.get("required_match_percentage", 0) >= 80:
            strengths.append({
                "area": "Required Skills",
                "score": skill_analysis["required_match_percentage"],
                "description": f"Strong match on required skills ({len(skill_analysis.get('required_skills_matched', []))} out of {skill_analysis.get('total_required_skills', 0)} matched)"
            })

        if experience_analysis.get("exceeds_preferred", False):
            strengths.append({
                "area": "Experience",
                "score": experience_analysis["experience_score"],
                "description": f"Exceeds preferred experience ({experience_analysis.get('total_years_experience', 0)} years)"
            })

        if experience_analysis.get("relevant_years_experience", 0) >= experience_analysis.get("required_years", 0):
            strengths.append({
                "area": "Relevant Experience",
                "score": experience_analysis["relevance_score"],
                "description": f"Strong relevant experience ({experience_analysis.get('relevant_years_experience', 0)} years in relevant roles)"
            })

        if education_match.get("meets_requirement", False):
            strengths.append({
                "area": "Education",
                "score": education_match["score"],
                "description": "Meets or exceeds education requirements"
            })

        if skill_analysis.get("preferred_match_percentage", 0) >= 70:
            strengths.append({
                "area": "Preferred Skills",
                "score": skill_analysis["preferred_match_percentage"],
                "description": f"Strong match on preferred skills ({len(skill_analysis.get('preferred_skills_matched', []))} matched)"
            })

        return strengths

def get_job_matcher():
    return JobMatcherManager()

