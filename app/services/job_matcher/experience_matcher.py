from typing import Dict, List, Any
from datetime import datetime
import re

class ExperienceMatcher:
    def match_experience(
        self,
        candidate_experience: List[Dict[str, Any]],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        total_years = self._calculate_total_experience(candidate_experience)
        required_years = job_requirements.get("experience_required", 0)
        preferred_years = job_requirements.get("experience_preferred", 0)

        relevant_experience = self._find_relevant_experience(
            candidate_experience,
            job_requirements.get("technologies", []),
            job_requirements.get("industry", "")
        )

        relevant_years = self._calculate_total_experience(relevant_experience)

        if required_years > 0:
            meets_minimum = total_years >= required_years
            experience_score = min((total_years / required_years) * 100, 100)
        else:
            meets_minimum = True
            experience_score = 100

        exceeds_preferred = total_years >= preferred_years if preferred_years > 0 else True

        relevance_score = self._calculate_relevance_score(
            relevant_years,
            required_years if required_years > 0 else 1
        )

        overall_experience_score = (experience_score * 0.6 + relevance_score * 0.4)

        return {
            "total_years_experience": round(total_years, 1),
            "relevant_years_experience": round(relevant_years, 1),
            "required_years": required_years,
            "preferred_years": preferred_years,
            "meets_minimum_requirement": meets_minimum,
            "exceeds_preferred": exceeds_preferred,
            "experience_score": round(experience_score, 2),
            "relevance_score": round(relevance_score, 2),
            "overall_experience_score": round(overall_experience_score, 2),
            "relevant_roles": [exp.get("title", "") for exp in relevant_experience]
        }

    def _calculate_total_experience(self, experiences: List[Dict[str, Any]]) -> float:
        total_months = 0
        for exp in experiences:
            months = self._calculate_duration_months(exp)
            total_months += months
        return total_months / 12.0

    def _calculate_duration_months(self, experience: Dict[str, Any]) -> int:
        try:
            start_date = self._parse_date(experience.get("start_date", ""))
            end_date = experience.get("end_date")

            if not start_date:
                return 0

            if not end_date or end_date.lower() in ["present", "current", "now"]:
                end_date = datetime.now()
            else:
                end_date = self._parse_date(end_date)

            if isinstance(end_date, datetime) and isinstance(start_date, datetime):
                delta = end_date - start_date
                return max(delta.days // 30, 0)

            return 0
        except:
            return 12

    def _parse_date(self, date_str: str) -> datetime:
        if not date_str:
            return None

        try:
            if re.match(r'^\d{4}$', str(date_str)):
                return datetime(int(date_str), 1, 1)
            elif re.match(r'^\d{4}-\d{2}$', str(date_str)):
                year, month = date_str.split('-')
                return datetime(int(year), int(month), 1)
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', str(date_str)):
                return datetime.fromisoformat(date_str)
            else:
                return None
        except:
            return None

    def _find_relevant_experience(
        self,
        experiences: List[Dict[str, Any]],
        technologies: List[str],
        industry: str
    ) -> List[Dict[str, Any]]:
        relevant = []
        tech_keywords = [t.lower() for t in technologies]

        for exp in experiences:
            is_relevant = False

            description = (exp.get("description", "") or "").lower()
            company = (exp.get("company", "") or "").lower()
            title = (exp.get("title", "") or "").lower()
            exp_technologies = exp.get("technologies", [])

            if exp_technologies:
                exp_tech_lower = [t.lower() for t in exp_technologies]
                if any(tech in exp_tech_lower for tech in tech_keywords):
                    is_relevant = True

            if industry and industry.lower() in company:
                is_relevant = True

            for tech in tech_keywords:
                if tech in description or tech in title:
                    is_relevant = True
                    break

            if is_relevant:
                relevant.append(exp)

        return relevant

    def _calculate_relevance_score(self, relevant_years: float, required_years: float) -> float:
        if required_years == 0:
            return 100

        score = (relevant_years / required_years) * 100
        return min(score, 100)

