from typing import Dict, Any
import json
from app.utils.openai_client import OpenAIClient
import logging
import re

logger = logging.getLogger(__name__)

class MatchScorer:
    def __init__(self):
        self.llm = OpenAIClient()

    def calculate_overall_score(
        self,
        skill_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any],
        education_match: Dict[str, Any]
    ) -> Dict[str, Any]:
        skill_score = skill_analysis.get("overall_skill_score", 0)
        experience_score = experience_analysis.get("overall_experience_score", 0)
        education_score = education_match.get("score", 0)

        weights = {
            "skills": 0.5,
            "experience": 0.3,
            "education": 0.2
        }

        overall_score = (
            skill_score * weights["skills"] +
            experience_score * weights["experience"] +
            education_score * weights["education"]
        )

        recommendation = self._get_recommendation(overall_score)
        confidence = self._calculate_confidence(skill_analysis, experience_analysis)

        return {
            "overall_score": round(overall_score, 2),
            "recommendation": recommendation,
            "confidence_score": round(confidence, 2),
            "category_scores": {
                "skills": round(skill_score, 2),
                "experience": round(experience_score, 2),
                "education": round(education_score, 2)
            },
            "weights_used": weights
        }

    def generate_gap_analysis(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        skill_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            prompt = f"""Analyze the gaps between this candidate's qualifications and the job requirements.

Candidate Skills: {json.dumps(resume_data.get('skills', {}))}
Job Required Skills: {json.dumps(job_requirements.get('required_skills', []))}
Missing Required Skills: {json.dumps(skill_analysis.get('required_skills_missing', []))}
Missing Preferred Skills: {json.dumps(skill_analysis.get('preferred_skills_missing', []))}

Candidate Experience: {experience_analysis.get('total_years_experience', 0)} years total, {experience_analysis.get('relevant_years_experience', 0)} years relevant
Required Experience: {job_requirements.get('experience_required', 0)} years

Generate a gap analysis in JSON format:
- critical_gaps: List of must-have requirements not met
- skill_gaps: Missing technical skills with severity (high/medium/low)
- experience_gaps: Experience-related gaps
- education_gaps: Education-related gaps
- recommendations: Top 3-5 specific actions to close gaps
- estimated_time_to_ready: Estimated months to become job-ready

Return ONLY valid JSON."""

            result = self.llm.invoke(prompt, temperature=0.3).strip()
            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            gap_analysis = json.loads(result)
            return gap_analysis

        except Exception as e:
            logger.error(f"Error generating gap analysis: {e}")
            return {
                "critical_gaps": skill_analysis.get('required_skills_missing', []),
                "skill_gaps": [],
                "experience_gaps": [],
                "education_gaps": [],
                "recommendations": ["Acquire missing required skills", "Gain more relevant experience"],
                "estimated_time_to_ready": "Unknown"
            }

    def _get_recommendation(self, score: float) -> str:
        if score >= 85:
            return "Excellent Match"
        elif score >= 70:
            return "Strong Match"
        elif score >= 55:
            return "Good Match"
        elif score >= 40:
            return "Moderate Match"
        else:
            return "Weak Match"

    def _calculate_confidence(
        self,
        skill_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any]
    ) -> float:
        skill_completeness = 1.0
        if skill_analysis.get("total_required_skills", 0) > 0:
            matched = len(skill_analysis.get("required_skills_matched", []))
            total = skill_analysis.get("total_required_skills", 1)
            skill_completeness = matched / total

        experience_confidence = 1.0 if experience_analysis.get("meets_minimum_requirement", False) else 0.5

        confidence = (skill_completeness * 0.6 + experience_confidence * 0.4) * 100
        return min(confidence, 99.9)

