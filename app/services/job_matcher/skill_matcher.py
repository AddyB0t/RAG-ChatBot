from typing import Dict, List, Any, Set
import re

class SkillMatcher:
    def match_skills(
        self,
        candidate_skills: Dict[str, List[str]],
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> Dict[str, Any]:
        all_candidate_skills = self._flatten_candidate_skills(candidate_skills)

        required_matched = self._calculate_matches(all_candidate_skills, required_skills)
        preferred_matched = self._calculate_matches(all_candidate_skills, preferred_skills)

        required_missing = [skill for skill in required_skills if not self._skill_exists(skill, all_candidate_skills)]
        preferred_missing = [skill for skill in preferred_skills if not self._skill_exists(skill, all_candidate_skills)]

        required_score = (len(required_matched) / len(required_skills) * 100) if required_skills else 100
        preferred_score = (len(preferred_matched) / len(preferred_skills) * 100) if preferred_skills else 100

        overall_skill_score = (required_score * 0.7 + preferred_score * 0.3)

        return {
            "required_skills_matched": required_matched,
            "required_skills_missing": required_missing,
            "required_match_percentage": round(required_score, 2),
            "preferred_skills_matched": preferred_matched,
            "preferred_skills_missing": preferred_missing,
            "preferred_match_percentage": round(preferred_score, 2),
            "overall_skill_score": round(overall_skill_score, 2),
            "total_candidate_skills": len(all_candidate_skills),
            "total_required_skills": len(required_skills),
            "total_preferred_skills": len(preferred_skills)
        }

    def _flatten_candidate_skills(self, candidate_skills: Dict[str, List[str]]) -> Set[str]:
        all_skills = set()
        for skill_type, skills in candidate_skills.items():
            if isinstance(skills, list):
                all_skills.update([s.lower() for s in skills if s])
        return all_skills

    def _calculate_matches(self, candidate_skills: Set[str], required_skills: List[str]) -> List[str]:
        matched = []
        for req_skill in required_skills:
            if self._skill_exists(req_skill, candidate_skills):
                matched.append(req_skill)
        return matched

    def _skill_exists(self, skill: str, candidate_skills: Set[str]) -> bool:
        skill_lower = skill.lower()

        if skill_lower in candidate_skills:
            return True

        skill_normalized = re.sub(r'[^\w\s]', '', skill_lower)
        for candidate_skill in candidate_skills:
            candidate_normalized = re.sub(r'[^\w\s]', '', candidate_skill)
            if skill_normalized == candidate_normalized:
                return True
            if skill_normalized in candidate_normalized or candidate_normalized in skill_normalized:
                return True

        return False

