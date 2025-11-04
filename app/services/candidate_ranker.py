"""
Candidate Ranking System
Ranks multiple candidates for a job position using multi-criteria analysis
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)

class CandidateRanker:
    """Ranks candidates for job positions using multi-criteria analysis"""

    DEFAULT_WEIGHTS = {
        'skills_match': 0.30,
        'experience_match': 0.25,
        'education_match': 0.15,
        'cultural_fit': 0.10,
        'career_trajectory': 0.10,
        'certifications': 0.05,
        'availability': 0.05
    }

    def __init__(self):
        """Initialize candidate ranker"""
        logger.info("Candidate Ranker initialized")

    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        job_requirements: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Rank candidates for a job position

        Args:
            candidates: List of candidate data with resume info and match scores
            job_requirements: Job requirements
            weights: Custom weights for ranking criteria (optional)

        Returns:
            Ranked candidates with detailed scoring
        """
        logger.info(f"Starting candidate ranking for {len(candidates)} candidates")

        if weights is None:
            weights = self.DEFAULT_WEIGHTS

        ranked_candidates = []
        for candidate in candidates:
            ranking_data = self._calculate_candidate_ranking(
                candidate,
                job_requirements,
                weights
            )
            ranked_candidates.append(ranking_data)

        ranked_candidates.sort(key=lambda x: x['final_score'], reverse=True)

        for i, candidate in enumerate(ranked_candidates):
            candidate['rank'] = i + 1
            candidate['percentile'] = ((len(ranked_candidates) - i) / len(ranked_candidates) * 100)

        tiers = self._assign_tiers(ranked_candidates)

        statistics_data = self._calculate_statistics(ranked_candidates)

        return {
            'total_candidates': len(ranked_candidates),
            'ranked_candidates': ranked_candidates,
            'tier_distribution': tiers,
            'statistics': statistics_data,
            'weights_used': weights,
            'ranking_criteria': list(weights.keys()),
            'ranked_at': datetime.utcnow().isoformat()
        }

    def _calculate_candidate_ranking(
        self,
        candidate: Dict[str, Any],
        job_requirements: Dict[str, Any],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate comprehensive ranking score for a candidate"""
        resume_data = candidate.get('resume_data', {})
        match_data = candidate.get('match_data', {})

        scores = {
            'skills_match': self._score_skills_match(resume_data, job_requirements, match_data),
            'experience_match': self._score_experience_match(resume_data, job_requirements),
            'education_match': self._score_education_match(resume_data, job_requirements),
            'cultural_fit': self._score_cultural_fit(resume_data, job_requirements),
            'career_trajectory': self._score_career_trajectory(resume_data),
            'certifications': self._score_certifications(resume_data),
            'availability': self._score_availability(candidate)
        }

        final_score = sum(scores[key] * weights.get(key, 0) for key in scores.keys())

        strengths, weaknesses = self._identify_candidate_strengths_weaknesses(scores, weights)

        return {
            'candidate_id': candidate.get('resume_id', 'unknown'),
            'candidate_name': self._get_candidate_name(resume_data),
            'final_score': round(final_score, 2),
            'category_scores': scores,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendation': self._generate_recommendation(final_score, strengths, weaknesses),
            'interview_priority': self._determine_interview_priority(final_score, scores),
            'match_summary': match_data.get('overall_score', 0)
        }

    def _score_skills_match(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        match_data: Dict[str, Any]
    ) -> float:
        """Score skills match (0-100)"""
        skill_analysis = match_data.get('skill_analysis', {})

        if skill_analysis:
            required_match = skill_analysis.get('required_match_percentage', 0)
            preferred_match = skill_analysis.get('preferred_match_percentage', 0)
            return required_match * 0.7 + preferred_match * 0.3

        candidate_skills = resume_data.get('skills', {})
        required_skills = job_requirements.get('required_skills', [])

        if not required_skills:
            return 50

        all_candidate_skills = []
        if isinstance(candidate_skills, dict):
            for skill_list in candidate_skills.values():
                if isinstance(skill_list, list):
                    all_candidate_skills.extend([s.lower() for s in skill_list])
        elif isinstance(candidate_skills, list):
            all_candidate_skills = [s.lower() for s in candidate_skills]

        required_skills_lower = [s.lower() for s in required_skills]
        matches = len([s for s in all_candidate_skills if s in required_skills_lower])

        return (matches / len(required_skills) * 100) if required_skills else 50

    def _score_experience_match(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> float:
        """Score experience match (0-100)"""
        experience = resume_data.get('experience', [])

        total_years = 0
        for exp in experience:
            years = exp.get('duration_years', 0) or 0
            total_years += years

        required_years = job_requirements.get('required_years', 3)

        if total_years >= required_years * 1.5:
            return 100
        elif total_years >= required_years:
            return 85
        elif total_years >= required_years * 0.7:
            return 65
        elif total_years >= required_years * 0.5:
            return 45
        else:
            return 25

    def _score_education_match(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> float:
        """Score education match (0-100)"""
        education = resume_data.get('education', [])
        required_education = job_requirements.get('education_required', '')

        if not required_education:
            return 75

        education_levels = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'mba': 4,
            'phd': 5,
            'doctorate': 5
        }

        required_level = 0
        for level, value in education_levels.items():
            if level in required_education.lower():
                required_level = max(required_level, value)

        candidate_level = 0
        for edu in education:
            degree = (edu.get('degree', '') or '').lower()
            for level, value in education_levels.items():
                if level in degree:
                    candidate_level = max(candidate_level, value)

        if candidate_level >= required_level:
            return 100
        elif candidate_level == required_level - 1:
            return 70
        elif candidate_level > 0:
            return 40
        else:
            return 20

    def _score_cultural_fit(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> float:
        """Score cultural fit based on soft skills and values (0-100)"""
        candidate_skills = resume_data.get('skills', {})
        soft_skills = []

        if isinstance(candidate_skills, dict):
            soft_skills = [s.lower() for s in candidate_skills.get('soft', [])]

        desired_soft_skills = ['communication', 'teamwork', 'leadership', 'problem solving', 'adaptability']

        if not soft_skills:
            return 50

        match_count = len([s for s in soft_skills if any(ds in s for ds in desired_soft_skills)])

        base_score = (match_count / len(desired_soft_skills) * 100)

        experience = resume_data.get('experience', [])
        team_experience = sum(
            1 for exp in experience
            if any(word in (exp.get('description', '') or '').lower()
                   for word in ['team', 'collaborate', 'led', 'managed'])
        )

        bonus = min(team_experience * 10, 20)

        return min(base_score + bonus, 100)

    def _score_career_trajectory(self, resume_data: Dict[str, Any]) -> float:
        """Score career trajectory and growth (0-100)"""
        experience = resume_data.get('experience', [])

        if len(experience) < 2:
            return 50

        sorted_exp = sorted(
            [exp for exp in experience if exp.get('start_date')],
            key=lambda x: x.get('start_date', ''),
            reverse=True
        )

        score = 50

        titles = [exp.get('title', '').lower() for exp in sorted_exp]

        promotion_indicators = ['senior', 'lead', 'principal', 'manager', 'director', 'head', 'vp', 'chief']

        seniority_levels = []
        for title in titles:
            level = sum(1 for indicator in promotion_indicators if indicator in title)
            seniority_levels.append(level)

        if len(seniority_levels) >= 2:
            recent_levels = seniority_levels[:3]
            if recent_levels[0] > recent_levels[-1]:
                score += 30
            elif recent_levels[0] == recent_levels[-1]:
                score += 15

        if len(experience) >= 3:
            score += 10

        avg_tenure = sum(exp.get('duration_years', 0) or 0 for exp in experience) / len(experience)
        if 2 <= avg_tenure <= 4:
            score += 10
        elif avg_tenure > 4:
            score += 5

        return min(score, 100)

    def _score_certifications(self, resume_data: Dict[str, Any]) -> float:
        """Score professional certifications (0-100)"""
        certifications = resume_data.get('certifications', [])

        if not certifications:
            return 30

        cert_count = len(certifications)

        if cert_count >= 5:
            return 100
        elif cert_count >= 3:
            return 85
        elif cert_count >= 2:
            return 70
        elif cert_count >= 1:
            return 55
        else:
            return 30

    def _score_availability(self, candidate: Dict[str, Any]) -> float:
        """Score candidate availability (0-100)"""
        availability = candidate.get('availability', 'unknown')

        availability_scores = {
            'immediate': 100,
            'within_2_weeks': 90,
            'within_1_month': 80,
            'within_2_months': 60,
            'within_3_months': 40,
            'unknown': 50
        }

        return availability_scores.get(availability.lower(), 50)

    def _get_candidate_name(self, resume_data: Dict[str, Any]) -> str:
        """Get candidate name from resume data"""
        personal_info = resume_data.get('personal_info', {})
        return personal_info.get('full_name', 'Unknown Candidate')

    def _identify_candidate_strengths_weaknesses(
        self,
        scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """Identify candidate strengths and weaknesses"""
        strengths = []
        weaknesses = []

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for category, score in sorted_scores[:3]:
            if score >= 75:
                strengths.append(f"{category.replace('_', ' ').title()}: {score:.0f}%")

        for category, score in sorted_scores[-3:]:
            if score < 60 and weights.get(category, 0) >= 0.10:
                weaknesses.append(f"{category.replace('_', ' ').title()}: {score:.0f}%")

        if not strengths:
            strengths = ["Balanced skill set"]

        if not weaknesses:
            weaknesses = ["No significant weaknesses identified"]

        return strengths, weaknesses

    def _generate_recommendation(
        self,
        final_score: float,
        strengths: List[str],
        weaknesses: List[str]
    ) -> str:
        """Generate hiring recommendation"""
        if final_score >= 85:
            return "STRONG RECOMMEND - Top-tier candidate, schedule interview immediately"
        elif final_score >= 70:
            return "RECOMMEND - Strong candidate, proceed with interview"
        elif final_score >= 55:
            return "CONSIDER - Meets basic requirements, interview if pipeline permits"
        elif final_score >= 40:
            return "MAYBE - Below target, consider only if limited options"
        else:
            return "NOT RECOMMENDED - Significant gaps in qualifications"

    def _determine_interview_priority(
        self,
        final_score: float,
        scores: Dict[str, float]
    ) -> str:
        """Determine interview priority"""
        skills_score = scores.get('skills_match', 0)
        experience_score = scores.get('experience_match', 0)

        if final_score >= 85 and skills_score >= 80:
            return "urgent"
        elif final_score >= 70:
            return "high"
        elif final_score >= 55:
            return "medium"
        else:
            return "low"

    def _assign_tiers(self, ranked_candidates: List[Dict[str, Any]]) -> Dict[str, int]:
        """Assign candidates to tiers"""
        tiers = {'S_tier': 0, 'A_tier': 0, 'B_tier': 0, 'C_tier': 0, 'D_tier': 0}

        for candidate in ranked_candidates:
            score = candidate['final_score']
            if score >= 90:
                candidate['tier'] = 'S'
                tiers['S_tier'] += 1
            elif score >= 75:
                candidate['tier'] = 'A'
                tiers['A_tier'] += 1
            elif score >= 60:
                candidate['tier'] = 'B'
                tiers['B_tier'] += 1
            elif score >= 45:
                candidate['tier'] = 'C'
                tiers['C_tier'] += 1
            else:
                candidate['tier'] = 'D'
                tiers['D_tier'] += 1

        return tiers

    def _calculate_statistics(self, ranked_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate ranking statistics"""
        scores = [c['final_score'] for c in ranked_candidates]

        if not scores:
            return {}

        return {
            'mean_score': round(statistics.mean(scores), 2),
            'median_score': round(statistics.median(scores), 2),
            'std_deviation': round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
            'min_score': round(min(scores), 2),
            'max_score': round(max(scores), 2),
            'score_range': round(max(scores) - min(scores), 2),
            'top_10_percent_cutoff': round(statistics.quantiles(scores, n=10)[-1], 2) if len(scores) >= 10 else max(scores),
            'qualified_candidates': len([s for s in scores if s >= 60]),
            'highly_qualified_candidates': len([s for s in scores if s >= 75])
        }

    def compare_candidates(
        self,
        candidate1: Dict[str, Any],
        candidate2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Direct comparison between two candidates

        Args:
            candidate1: First candidate data
            candidate2: Second candidate data

        Returns:
            Detailed comparison
        """
        score1 = candidate1.get('final_score', 0)
        score2 = candidate2.get('final_score', 0)

        structured1 = candidate1.get('structured_data', {})
        structured2 = candidate2.get('structured_data', {})

        if score1 == 0 and score2 == 0 and (structured1 or structured2):
            score1 = self._calculate_resume_quality_score(structured1)
            score2 = self._calculate_resume_quality_score(structured2)

        comparison = {
            'candidate1_score': score1,
            'candidate2_score': score2,
            'score_difference': abs(score1 - score2),
            'winner': 'candidate1' if score1 > score2 else ('candidate2' if score2 > score1 else 'tie'),
            'category_comparison': {},
            'resume_comparison': self._compare_resume_structures(structured1, structured2)
        }

        scores1 = candidate1.get('category_scores', {})
        scores2 = candidate2.get('category_scores', {})

        for category in scores1.keys():
            if category in scores2:
                comparison['category_comparison'][category] = {
                    'candidate1': scores1[category],
                    'candidate2': scores2[category],
                    'leader': 'candidate1' if scores1[category] > scores2[category] else 'candidate2',
                    'difference': abs(scores1[category] - scores2[category])
                }

        return comparison

    def _calculate_resume_quality_score(self, structured_data: Dict[str, Any]) -> float:
        """Calculate a quality score based on resume completeness and content"""
        if not structured_data:
            return 0.0

        score = 0.0

        personal_info = structured_data.get('personal_information', {})
        if personal_info.get('email'):
            score += 5
        if personal_info.get('phone'):
            score += 5
        if personal_info.get('location'):
            score += 5

        skills = structured_data.get('skills', [])
        score += min(len(skills) * 2, 20)

        experience = structured_data.get('work_experience', [])
        score += min(len(experience) * 10, 30)

        education = structured_data.get('education', [])
        score += min(len(education) * 8, 20)

        certifications = structured_data.get('certifications', [])
        score += min(len(certifications) * 3, 15)

        return min(score, 100.0)

    def _compare_resume_structures(self, structured1: Dict[str, Any], structured2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare resume structures"""
        return {
            'skills': {
                'candidate1_count': len(structured1.get('skills', [])),
                'candidate2_count': len(structured2.get('skills', [])),
                'leader': 'candidate1' if len(structured1.get('skills', [])) > len(structured2.get('skills', [])) else 'candidate2'
            },
            'experience': {
                'candidate1_count': len(structured1.get('work_experience', [])),
                'candidate2_count': len(structured2.get('work_experience', [])),
                'leader': 'candidate1' if len(structured1.get('work_experience', [])) > len(structured2.get('work_experience', [])) else 'candidate2'
            },
            'education': {
                'candidate1_count': len(structured1.get('education', [])),
                'candidate2_count': len(structured2.get('education', [])),
                'leader': 'candidate1' if len(structured1.get('education', [])) > len(structured2.get('education', [])) else 'candidate2'
            },
            'certifications': {
                'candidate1_count': len(structured1.get('certifications', [])),
                'candidate2_count': len(structured2.get('certifications', [])),
                'leader': 'candidate1' if len(structured1.get('certifications', [])) > len(structured2.get('certifications', [])) else 'candidate2'
            }
        }

_candidate_ranker_instance = None

def get_candidate_ranker() -> CandidateRanker:
    """Get or create candidate ranker instance (singleton)"""
    global _candidate_ranker_instance
    if _candidate_ranker_instance is None:
        _candidate_ranker_instance = CandidateRanker()
    return _candidate_ranker_instance
