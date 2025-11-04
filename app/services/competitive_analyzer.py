"""
Competitive Analysis for Job Matching
Analyzes candidate competitiveness against market standards and other candidates
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)

class CompetitiveAnalyzer:
    """Analyzes candidate competitiveness in the job market"""

    INDUSTRY_BENCHMARKS = {
        'software_engineering': {
            'avg_years_experience': 5,
            'common_skills': ['python', 'java', 'javascript', 'aws', 'docker', 'kubernetes'],
            'preferred_education': 'bachelor',
            'avg_salary_range': (80000, 150000)
        },
        'data_science': {
            'avg_years_experience': 4,
            'common_skills': ['python', 'r', 'sql', 'machine learning', 'tensorflow', 'pandas'],
            'preferred_education': 'master',
            'avg_salary_range': (90000, 160000)
        },
        'product_management': {
            'avg_years_experience': 6,
            'common_skills': ['agile', 'scrum', 'roadmap', 'analytics', 'stakeholder management'],
            'preferred_education': 'bachelor',
            'avg_salary_range': (95000, 170000)
        },
        'devops': {
            'avg_years_experience': 5,
            'common_skills': ['kubernetes', 'docker', 'jenkins', 'terraform', 'aws', 'ci/cd'],
            'preferred_education': 'bachelor',
            'avg_salary_range': (85000, 155000)
        },
        'default': {
            'avg_years_experience': 5,
            'common_skills': [],
            'preferred_education': 'bachelor',
            'avg_salary_range': (60000, 120000)
        }
    }

    def __init__(self):
        """Initialize competitive analyzer"""
        logger.info("Competitive Analyzer initialized")

    def analyze_competitiveness(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        match_score: float,
        other_candidates: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze candidate competitiveness

        Args:
            resume_data: Parsed resume data
            job_requirements: Job requirements
            match_score: Overall match score (0-100)
            other_candidates: Optional list of other candidate data for comparison

        Returns:
            Competitive analysis results
        """
        logger.info("Starting competitive analysis")

        industry = self._infer_industry(job_requirements)
        benchmarks = self.INDUSTRY_BENCHMARKS.get(industry, self.INDUSTRY_BENCHMARKS['default'])

        experience_competitiveness = self._analyze_experience_competitiveness(
            resume_data, benchmarks
        )

        skills_competitiveness = self._analyze_skills_competitiveness(
            resume_data, job_requirements, benchmarks
        )

        education_competitiveness = self._analyze_education_competitiveness(
            resume_data, benchmarks
        )

        market_position = self._calculate_market_position(
            match_score,
            experience_competitiveness,
            skills_competitiveness,
            education_competitiveness
        )

        strengths_weaknesses = self._identify_strengths_weaknesses(
            experience_competitiveness,
            skills_competitiveness,
            education_competitiveness
        )

        competitive_advantages = self._identify_competitive_advantages(
            resume_data, job_requirements, benchmarks
        )

        improvement_priorities = self._generate_improvement_priorities(
            strengths_weaknesses['weaknesses'],
            benchmarks
        )

        relative_ranking = None
        if other_candidates and len(other_candidates) > 0:
            relative_ranking = self._compare_with_candidates(
                resume_data,
                match_score,
                other_candidates
            )

        return {
            'competitive_score': market_position['score'],
            'market_position': market_position['position'],
            'industry_benchmark': industry,
            'experience_analysis': experience_competitiveness,
            'skills_analysis': skills_competitiveness,
            'education_analysis': education_competitiveness,
            'strengths': strengths_weaknesses['strengths'],
            'weaknesses': strengths_weaknesses['weaknesses'],
            'competitive_advantages': competitive_advantages,
            'improvement_priorities': improvement_priorities,
            'relative_ranking': relative_ranking,
            'market_insights': self._generate_market_insights(
                market_position, industry, benchmarks
            ),
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def _infer_industry(self, job_requirements: Dict[str, Any]) -> str:
        """Infer industry from job requirements"""
        title = (job_requirements.get('job_title', '') or '').lower()
        description = (job_requirements.get('description', '') or '').lower()
        skills = [s.lower() for s in job_requirements.get('required_skills', [])]

        text = f"{title} {description} {' '.join(skills)}"

        if any(term in text for term in ['software', 'developer', 'engineer', 'programming']):
            return 'software_engineering'
        elif any(term in text for term in ['data science', 'machine learning', 'ai', 'analytics']):
            return 'data_science'
        elif any(term in text for term in ['product manager', 'product owner', 'pm']):
            return 'product_management'
        elif any(term in text for term in ['devops', 'sre', 'infrastructure', 'cloud engineer']):
            return 'devops'
        else:
            return 'default'

    def _analyze_experience_competitiveness(
        self,
        resume_data: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze experience competitiveness"""
        experience = resume_data.get('experience', [])

        total_years = 0
        for exp in experience:
            years = exp.get('duration_years', 0) or 0
            total_years += years

        avg_years = benchmarks['avg_years_experience']
        percentage = (total_years / avg_years * 100) if avg_years > 0 else 0

        if total_years >= avg_years * 1.5:
            level = 'highly_competitive'
            score = 95
        elif total_years >= avg_years:
            level = 'competitive'
            score = 80
        elif total_years >= avg_years * 0.7:
            level = 'moderately_competitive'
            score = 60
        else:
            level = 'below_average'
            score = 40

        return {
            'total_years': round(total_years, 1),
            'benchmark_years': avg_years,
            'percentage_of_benchmark': round(percentage, 1),
            'competitiveness_level': level,
            'score': score,
            'gap_years': max(0, avg_years - total_years)
        }

    def _analyze_skills_competitiveness(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze skills competitiveness"""
        candidate_skills = resume_data.get('skills', {})
        all_candidate_skills = []

        if isinstance(candidate_skills, dict):
            for skill_list in candidate_skills.values():
                if isinstance(skill_list, list):
                    all_candidate_skills.extend([s.lower() for s in skill_list])
        elif isinstance(candidate_skills, list):
            all_candidate_skills = [s.lower() for s in candidate_skills]

        common_industry_skills = [s.lower() for s in benchmarks.get('common_skills', [])]
        required_job_skills = [s.lower() for s in job_requirements.get('required_skills', [])]

        industry_match = len([s for s in all_candidate_skills if s in common_industry_skills])
        industry_coverage = (industry_match / len(common_industry_skills) * 100) if common_industry_skills else 0

        job_match = len([s for s in all_candidate_skills if s in required_job_skills])
        job_coverage = (job_match / len(required_job_skills) * 100) if required_job_skills else 0

        overall_score = (industry_coverage * 0.4 + job_coverage * 0.6)

        if overall_score >= 80:
            level = 'highly_competitive'
        elif overall_score >= 60:
            level = 'competitive'
        elif overall_score >= 40:
            level = 'moderately_competitive'
        else:
            level = 'below_average'

        missing_industry_skills = [s for s in common_industry_skills if s not in all_candidate_skills]
        missing_job_skills = [s for s in required_job_skills if s not in all_candidate_skills]

        return {
            'total_skills': len(all_candidate_skills),
            'industry_coverage': round(industry_coverage, 1),
            'job_coverage': round(job_coverage, 1),
            'competitiveness_level': level,
            'score': round(overall_score, 1),
            'missing_industry_skills': missing_industry_skills[:5],
            'missing_job_skills': missing_job_skills[:5]
        }

    def _analyze_education_competitiveness(
        self,
        resume_data: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze education competitiveness"""
        education = resume_data.get('education', [])

        education_levels = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'mba': 4,
            'phd': 5,
            'doctorate': 5
        }

        preferred = benchmarks.get('preferred_education', 'bachelor')
        preferred_level = education_levels.get(preferred, 3)

        candidate_level = 0
        highest_degree = None
        for edu in education:
            degree = (edu.get('degree', '') or '').lower()
            for level_name, level_value in education_levels.items():
                if level_name in degree:
                    if level_value > candidate_level:
                        candidate_level = level_value
                        highest_degree = degree

        if candidate_level >= preferred_level + 1:
            level = 'highly_competitive'
            score = 95
        elif candidate_level >= preferred_level:
            level = 'competitive'
            score = 80
        elif candidate_level == preferred_level - 1:
            level = 'moderately_competitive'
            score = 60
        else:
            level = 'below_average'
            score = 40

        return {
            'highest_degree': highest_degree or 'Not specified',
            'degree_level': candidate_level,
            'preferred_level': preferred_level,
            'competitiveness_level': level,
            'score': score
        }

    def _calculate_market_position(
        self,
        match_score: float,
        experience_comp: Dict[str, Any],
        skills_comp: Dict[str, Any],
        education_comp: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate overall market position"""
        weights = {
            'match': 0.4,
            'experience': 0.25,
            'skills': 0.25,
            'education': 0.1
        }

        competitive_score = (
            match_score * weights['match'] +
            experience_comp['score'] * weights['experience'] +
            skills_comp['score'] * weights['skills'] +
            education_comp['score'] * weights['education']
        )

        if competitive_score >= 85:
            position = 'top_tier'
            description = 'Top 10% - Highly competitive candidate'
        elif competitive_score >= 70:
            position = 'strong'
            description = 'Top 25% - Strong competitive position'
        elif competitive_score >= 55:
            position = 'average'
            description = 'Top 50% - Average competitive position'
        else:
            position = 'below_average'
            description = 'Below average - Needs improvement'

        return {
            'score': round(competitive_score, 1),
            'position': position,
            'description': description,
            'percentile': self._score_to_percentile(competitive_score)
        }

    def _score_to_percentile(self, score: float) -> int:
        """Convert score to percentile"""
        if score >= 95:
            return 99
        elif score >= 85:
            return 90
        elif score >= 75:
            return 75
        elif score >= 65:
            return 60
        elif score >= 55:
            return 50
        elif score >= 45:
            return 40
        elif score >= 35:
            return 25
        else:
            return 10

    def _identify_strengths_weaknesses(
        self,
        experience_comp: Dict[str, Any],
        skills_comp: Dict[str, Any],
        education_comp: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Identify strengths and weaknesses"""
        strengths = []
        weaknesses = []

        if experience_comp['score'] >= 80:
            strengths.append(f"Strong experience ({experience_comp['total_years']} years)")
        elif experience_comp['score'] < 60:
            weaknesses.append(f"Limited experience ({experience_comp['gap_years']} years gap)")

        if skills_comp['score'] >= 80:
            strengths.append(f"Excellent skill coverage ({skills_comp['job_coverage']}% job match)")
        elif skills_comp['score'] < 60:
            weaknesses.append(f"Skill gaps ({len(skills_comp['missing_job_skills'])} key skills missing)")

        if education_comp['score'] >= 80:
            strengths.append(f"Strong educational background ({education_comp['highest_degree']})")
        elif education_comp['score'] < 60:
            weaknesses.append("Educational requirements not fully met")

        if not strengths:
            strengths.append("Demonstrates potential for growth")

        if not weaknesses:
            weaknesses.append("Minor areas for continued development")

        return {'strengths': strengths, 'weaknesses': weaknesses}

    def _identify_competitive_advantages(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Identify unique competitive advantages"""
        advantages = []

        certifications = resume_data.get('certifications', [])
        if len(certifications) >= 3:
            advantages.append({
                'advantage': 'Multiple Certifications',
                'description': f"{len(certifications)} professional certifications",
                'impact': 'high'
            })

        skills = resume_data.get('skills', {})
        if isinstance(skills, dict):
            languages = skills.get('languages', [])
            if len(languages) >= 2:
                advantages.append({
                    'advantage': 'Multilingual',
                    'description': f"Fluent in {len(languages)} languages",
                    'impact': 'medium'
                })

        experience = resume_data.get('experience', [])
        leadership_count = sum(
            1 for exp in experience
            if any(word in (exp.get('title', '') or '').lower()
                   for word in ['lead', 'manager', 'director', 'head', 'chief'])
        )
        if leadership_count >= 2:
            advantages.append({
                'advantage': 'Leadership Experience',
                'description': f"{leadership_count} leadership roles",
                'impact': 'high'
            })

        if not advantages:
            advantages.append({
                'advantage': 'Well-Rounded Profile',
                'description': 'Balanced skills and experience',
                'impact': 'medium'
            })

        return advantages

    def _generate_improvement_priorities(
        self,
        weaknesses: List[str],
        benchmarks: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate prioritized improvement recommendations"""
        priorities = []

        for weakness in weaknesses:
            if 'experience' in weakness.lower():
                priorities.append({
                    'priority': 'high',
                    'area': 'Experience',
                    'action': 'Seek additional project work or responsibilities',
                    'timeline': '6-12 months'
                })
            elif 'skill' in weakness.lower():
                priorities.append({
                    'priority': 'high',
                    'area': 'Skills',
                    'action': f"Learn key industry skills: {', '.join(benchmarks['common_skills'][:3])}",
                    'timeline': '3-6 months'
                })
            elif 'education' in weakness.lower():
                priorities.append({
                    'priority': 'medium',
                    'area': 'Education',
                    'action': 'Consider relevant certifications or advanced degree',
                    'timeline': '12+ months'
                })

        if not priorities:
            priorities.append({
                'priority': 'low',
                'area': 'Continuous Improvement',
                'action': 'Stay updated with industry trends and emerging technologies',
                'timeline': 'Ongoing'
            })

        return priorities

    def _compare_with_candidates(
        self,
        resume_data: Dict[str, Any],
        match_score: float,
        other_candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare candidate with others"""
        all_scores = [c.get('match_score', 0) for c in other_candidates] + [match_score]
        all_scores_sorted = sorted(all_scores, reverse=True)

        rank = all_scores_sorted.index(match_score) + 1
        total = len(all_scores)
        percentile = ((total - rank) / total * 100) if total > 1 else 100

        avg_score = statistics.mean(all_scores) if all_scores else 0
        median_score = statistics.median(all_scores) if all_scores else 0

        if rank <= total * 0.1:
            tier = 'top_tier'
        elif rank <= total * 0.25:
            tier = 'strong'
        elif rank <= total * 0.5:
            tier = 'average'
        else:
            tier = 'below_average'

        return {
            'rank': rank,
            'total_candidates': total,
            'percentile': round(percentile, 1),
            'tier': tier,
            'score_vs_average': round(match_score - avg_score, 1),
            'score_vs_median': round(match_score - median_score, 1),
            'top_candidate_score': all_scores_sorted[0] if all_scores_sorted else 0
        }

    def _generate_market_insights(
        self,
        market_position: Dict[str, Any],
        industry: str,
        benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Generate market insights"""
        insights = []

        position = market_position['position']
        if position == 'top_tier':
            insights.append("You are among the most competitive candidates in the market")
            insights.append("Consider negotiating for higher compensation or benefits")
        elif position == 'strong':
            insights.append("You have a strong competitive position")
            insights.append("Focus on highlighting your unique strengths in interviews")
        elif position == 'average':
            insights.append("You meet basic market expectations")
            insights.append("Consider developing additional skills to stand out")
        else:
            insights.append("Significant improvement needed to be competitive")
            insights.append("Focus on closing skill and experience gaps")

        salary_range = benchmarks.get('avg_salary_range', (0, 0))
        if salary_range[0] > 0:
            insights.append(
                f"Market salary range for this role: ${salary_range[0]:,} - ${salary_range[1]:,}"
            )

        return insights

_competitive_analyzer_instance = None

def get_competitive_analyzer() -> CompetitiveAnalyzer:
    """Get or create competitive analyzer instance (singleton)"""
    global _competitive_analyzer_instance
    if _competitive_analyzer_instance is None:
        _competitive_analyzer_instance = CompetitiveAnalyzer()
    return _competitive_analyzer_instance
