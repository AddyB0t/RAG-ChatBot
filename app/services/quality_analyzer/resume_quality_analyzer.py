import json
import re
from typing import Dict, Any
from app.utils.openrouter_client import OpenRouterClient
import logging

logger = logging.getLogger(__name__)

class ResumeQualityAnalyzer:
    """Analyzes resume quality and provides improvement suggestions"""

    def __init__(self):
        self.llm = OpenRouterClient()

    def analyze_quality(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall resume quality and completeness

        Returns:
            - quality_score: 0-100
            - completeness_score: 0-100
            - industry_classifications: list of industries
            - career_level: Entry/Mid/Senior/Executive
            - suggestions: improvement recommendations
        """
        try:
            prompt = f"""Analyze this resume data and provide a comprehensive quality assessment.

Resume Data:
{json.dumps(resume_data, indent=2)}

Provide analysis in JSON format:
{{
  "quality_score": <0-100 score based on formatting, clarity, impact>,
  "completeness_score": <0-100 score based on required sections>,
  "career_level": "<Entry/Mid/Senior/Executive>",
  "industry_classifications": ["industry1", "industry2"],
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "missing_sections": ["section1", "section2"],
  "suggestions": [
    {{"category": "Content", "priority": "high", "suggestion": "..."}},
    {{"category": "Skills", "priority": "medium", "suggestion": "..."}}
  ],
  "ats_compatibility_score": <0-100 score for ATS systems>,
  "keyword_density": {{"adequate": true/false, "missing_keywords": []}},
  "estimated_years_experience": <number>
}}

Return ONLY valid JSON."""

            result = self.llm.invoke(prompt, temperature=0.3).strip()
            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            analysis = json.loads(result)
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in quality analysis: {e}")
            return self._get_default_analysis()
        except Exception as e:
            logger.error(f"Error analyzing quality: {e}")
            return self._get_default_analysis()

    def estimate_salary_range(self, resume_data: Dict[str, Any], location: str = "US") -> Dict[str, Any]:
        """
        Estimate salary range based on skills, experience, and location
        """
        try:
            prompt = f"""Based on this resume data and location, estimate a realistic salary range.

Resume Data:
{json.dumps(resume_data, indent=2)}

Location: {location}

Provide estimation in JSON format:
{{
  "currency": "USD",
  "min_salary": <number>,
  "max_salary": <number>,
  "median_salary": <number>,
  "confidence": "<high/medium/low>",
  "factors": ["factor1", "factor2"],
  "market_demand": "<high/medium/low>",
  "growth_potential": "<high/medium/low>"
}}

Return ONLY valid JSON."""

            result = self.llm.invoke(prompt, temperature=0.3).strip()
            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            salary_estimate = json.loads(result)
            return salary_estimate

        except Exception as e:
            logger.error(f"Error estimating salary: {e}")
            return {
                "currency": "USD",
                "min_salary": 0,
                "max_salary": 0,
                "median_salary": 0,
                "confidence": "low",
                "factors": [],
                "market_demand": "unknown",
                "growth_potential": "unknown"
            }

    def generate_improvement_plan(self, resume_data: Dict[str, Any], target_role: str = None) -> Dict[str, Any]:
        """
        Generate a detailed improvement plan for the resume
        """
        try:
            target_clause = f"Target Role: {target_role}" if target_role else ""

            prompt = f"""Create a detailed improvement plan for this resume.

Resume Data:
{json.dumps(resume_data, indent=2)}

{target_clause}

Provide improvement plan in JSON format:
{{
  "priority_actions": [
    {{"action": "...", "impact": "high/medium/low", "effort": "easy/moderate/hard"}}
  ],
  "content_improvements": [
    {{"section": "experience", "current_issue": "...", "recommendation": "..."}}
  ],
  "skill_gaps": ["skill1", "skill2"],
  "recommended_certifications": ["cert1", "cert2"],
  "formatting_suggestions": ["suggestion1", "suggestion2"],
  "estimated_improvement_time": "<timeframe>",
  "expected_score_increase": "<percentage>"
}}

Return ONLY valid JSON."""

            result = self.llm.invoke(prompt, temperature=0.3).strip()
            result = re.sub(r'^```json\s*', '', result)
            result = re.sub(r'\s*```$', '', result)

            improvement_plan = json.loads(result)
            return improvement_plan

        except Exception as e:
            logger.error(f"Error generating improvement plan: {e}")
            return {
                "priority_actions": [],
                "content_improvements": [],
                "skill_gaps": [],
                "recommended_certifications": [],
                "formatting_suggestions": [],
                "estimated_improvement_time": "Unknown",
                "expected_score_increase": "Unknown"
            }

    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when AI fails"""
        return {
            "quality_score": 50,
            "completeness_score": 50,
            "career_level": "Unknown",
            "industry_classifications": [],
            "strengths": [],
            "weaknesses": [],
            "missing_sections": [],
            "suggestions": [],
            "ats_compatibility_score": 50,
            "keyword_density": {"adequate": False, "missing_keywords": []},
            "estimated_years_experience": 0
        }

_quality_analyzer_instance = None

def get_quality_analyzer():
    """Singleton pattern for quality analyzer"""
    global _quality_analyzer_instance
    if _quality_analyzer_instance is None:
        _quality_analyzer_instance = ResumeQualityAnalyzer()
    return _quality_analyzer_instance

