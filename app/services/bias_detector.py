"""
Bias Detection for Resumes
Detects potential biases in resume content and job descriptions
"""
import logging
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class BiasDetector:
    """Detects potential biases in resume content and job descriptions"""

    GENDER_INDICATORS = {
        'male': ['he', 'him', 'his', 'mr', 'gentleman', 'guy', 'bro', 'dude', 'fraternity'],
        'female': ['she', 'her', 'hers', 'ms', 'mrs', 'miss', 'lady', 'gal', 'girl', 'sorority'],
        'neutral': ['they', 'them', 'their', 'person', 'individual', 'candidate', 'professional']
    }

    AGE_INDICATORS = {
        'young': [
            'recent graduate', 'entry level', 'young', 'energetic', 'fresh',
            'digital native', 'millennial', 'gen z', 'new grad'
        ],
        'mature': [
            'experienced', 'seasoned', 'senior', 'veteran', 'mature',
            'established', 'traditional', 'baby boomer'
        ]
    }

    CULTURAL_INDICATORS = {
        'ethnic': [
            'native speaker', 'cultural fit', 'local', 'heritage',
            'traditional name', 'foreign', 'international', 'exotic'
        ],
        'religious': [
            'christian', 'muslim', 'jewish', 'hindu', 'buddhist',
            'religious', 'faith-based', 'church', 'temple', 'mosque'
        ]
    }

    SOCIOECONOMIC_INDICATORS = [
        'prestigious university', 'elite', 'top-tier', 'ivy league',
        'privileged', 'upper class', 'exclusive', 'private school'
    ]

    DISABILITY_INDICATORS = [
        'disabled', 'handicapped', 'wheelchair', 'blind', 'deaf',
        'impaired', 'special needs', 'accommodation', 'disability'
    ]

    FAMILY_STATUS_INDICATORS = [
        'single', 'married', 'divorced', 'mother', 'father', 'parent',
        'children', 'family', 'spouse', 'pregnant', 'maternity', 'paternity'
    ]

    APPEARANCE_INDICATORS = [
        'attractive', 'presentable', 'well-groomed', 'professional appearance',
        'good-looking', 'physical fitness', 'image', 'looks'
    ]

    def __init__(self):
        """Initialize bias detector"""
        self.bias_patterns = self._compile_patterns()
        logger.info("Bias Detector initialized")

    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for bias detection"""
        patterns = {}

        all_indicators = {
            'gender': [word for words in self.GENDER_INDICATORS.values() for word in words],
            'age': [word for words in self.AGE_INDICATORS.values() for word in words],
            'cultural': [word for words in self.CULTURAL_INDICATORS.values() for word in words],
            'socioeconomic': self.SOCIOECONOMIC_INDICATORS,
            'disability': self.DISABILITY_INDICATORS,
            'family_status': self.FAMILY_STATUS_INDICATORS,
            'appearance': self.APPEARANCE_INDICATORS
        }

        for category, indicators in all_indicators.items():
            patterns[category] = [
                re.compile(r'\b' + re.escape(indicator) + r'\b', re.IGNORECASE)
                for indicator in indicators
            ]

        return patterns

    def detect_bias_in_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect potential biases in resume content

        Args:
            resume_data: Parsed resume data

        Returns:
            Bias detection results
        """
        logger.info("Starting bias detection for resume")

        text_content = self._extract_text_from_resume(resume_data)

        biases_found = []
        bias_score = 0

        for category, patterns in self.bias_patterns.items():
            matches = self._find_pattern_matches(text_content, patterns)
            if matches:
                bias_info = {
                    'category': category,
                    'severity': self._calculate_severity(category, len(matches)),
                    'matches': matches,
                    'count': len(matches),
                    'description': self._get_bias_description(category),
                    'recommendation': self._get_bias_recommendation(category)
                }
                biases_found.append(bias_info)
                bias_score += len(matches) * self._get_category_weight(category)

        overall_risk = self._calculate_overall_risk(bias_score, biases_found)

        return {
            'has_bias': len(biases_found) > 0,
            'bias_score': min(bias_score, 100),
            'overall_risk': overall_risk,
            'biases_detected': biases_found,
            'total_bias_indicators': sum(b['count'] for b in biases_found),
            'categories_affected': list(set(b['category'] for b in biases_found)),
            'recommendations': self._generate_recommendations(biases_found),
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def detect_bias_in_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Detect potential biases in job description

        Args:
            job_description: Job description text

        Returns:
            Bias detection results
        """
        logger.info("Starting bias detection for job description")

        biases_found = []
        bias_score = 0

        for category, patterns in self.bias_patterns.items():
            matches = self._find_pattern_matches(job_description, patterns)
            if matches:
                bias_info = {
                    'category': category,
                    'severity': self._calculate_severity(category, len(matches)),
                    'matches': matches,
                    'count': len(matches),
                    'description': self._get_bias_description(category),
                    'recommendation': self._get_bias_recommendation(category)
                }
                biases_found.append(bias_info)
                bias_score += len(matches) * self._get_category_weight(category)

        overall_risk = self._calculate_overall_risk(bias_score, biases_found)

        inclusive_language_score = self._check_inclusive_language(job_description)

        return {
            'has_bias': len(biases_found) > 0,
            'bias_score': min(bias_score, 100),
            'overall_risk': overall_risk,
            'biases_detected': biases_found,
            'total_bias_indicators': sum(b['count'] for b in biases_found),
            'categories_affected': list(set(b['category'] for b in biases_found)),
            'inclusive_language_score': inclusive_language_score,
            'recommendations': self._generate_recommendations(biases_found),
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def _extract_text_from_resume(self, resume_data: Dict[str, Any]) -> str:
        """Extract all text content from resume data"""
        text_parts = []

        if 'personal_info' in resume_data:
            personal_info = resume_data['personal_info']
            if personal_info.get('full_name'):
                text_parts.append(personal_info['full_name'])
            if personal_info.get('summary'):
                text_parts.append(personal_info['summary'])

        if 'experience' in resume_data:
            for exp in resume_data['experience']:
                if exp.get('title'):
                    text_parts.append(exp['title'])
                if exp.get('company'):
                    text_parts.append(exp['company'])
                if exp.get('description'):
                    text_parts.append(exp['description'])

        if 'education' in resume_data:
            for edu in resume_data['education']:
                if edu.get('institution'):
                    text_parts.append(edu['institution'])
                if edu.get('degree'):
                    text_parts.append(edu['degree'])
                if edu.get('field'):
                    text_parts.append(edu['field'])

        if 'skills' in resume_data:
            skills = resume_data['skills']
            if isinstance(skills, dict):
                for skill_list in skills.values():
                    if isinstance(skill_list, list):
                        text_parts.extend(skill_list)
            elif isinstance(skills, list):
                text_parts.extend(skills)

        return ' '.join(str(part) for part in text_parts if part)

    def _find_pattern_matches(self, text: str, patterns: List[re.Pattern]) -> List[str]:
        """Find all pattern matches in text"""
        matches = []
        for pattern in patterns:
            found = pattern.findall(text)
            matches.extend(found)
        return list(set(matches))

    def _calculate_severity(self, category: str, match_count: int) -> str:
        """Calculate severity level based on category and match count"""
        high_severity_categories = ['gender', 'age', 'cultural', 'disability']

        if category in high_severity_categories:
            if match_count >= 3:
                return 'high'
            elif match_count >= 2:
                return 'medium'
            else:
                return 'low'
        else:
            if match_count >= 5:
                return 'high'
            elif match_count >= 3:
                return 'medium'
            else:
                return 'low'

    def _get_category_weight(self, category: str) -> int:
        """Get weight for each bias category"""
        weights = {
            'gender': 15,
            'age': 12,
            'cultural': 12,
            'disability': 15,
            'family_status': 10,
            'appearance': 8,
            'socioeconomic': 8
        }
        return weights.get(category, 5)

    def _calculate_overall_risk(self, bias_score: int, biases_found: List[Dict]) -> str:
        """Calculate overall risk level"""
        high_severity_count = sum(1 for b in biases_found if b['severity'] == 'high')

        if bias_score >= 40 or high_severity_count >= 2:
            return 'high'
        elif bias_score >= 20 or len(biases_found) >= 3:
            return 'medium'
        elif len(biases_found) > 0:
            return 'low'
        else:
            return 'none'

    def _get_bias_description(self, category: str) -> str:
        """Get description for bias category"""
        descriptions = {
            'gender': 'Gender-specific language that may discriminate based on gender',
            'age': 'Age-related language that may discriminate based on age',
            'cultural': 'Cultural or ethnic references that may create bias',
            'disability': 'Language related to disabilities that may be discriminatory',
            'family_status': 'References to family or marital status',
            'appearance': 'Physical appearance requirements that may be discriminatory',
            'socioeconomic': 'Socioeconomic indicators that may create bias'
        }
        return descriptions.get(category, 'Potential bias detected')

    def _get_bias_recommendation(self, category: str) -> str:
        """Get recommendation for addressing bias"""
        recommendations = {
            'gender': 'Use gender-neutral language (they/them) and avoid gender-specific terms',
            'age': 'Focus on skills and experience rather than age-related descriptors',
            'cultural': 'Use inclusive language that welcomes all cultural backgrounds',
            'disability': 'Avoid disability-related language unless directly relevant to job requirements',
            'family_status': 'Remove references to marital or family status',
            'appearance': 'Focus on professional qualifications rather than physical appearance',
            'socioeconomic': 'Avoid language that implies socioeconomic requirements'
        }
        return recommendations.get(category, 'Review and remove biased language')

    def _generate_recommendations(self, biases_found: List[Dict]) -> List[str]:
        """Generate overall recommendations for addressing biases"""
        if not biases_found:
            return ['No biases detected. Content appears to be inclusive and neutral.']

        recommendations = [
            'Review and revise content to remove biased language',
            'Use gender-neutral and age-neutral terminology',
            'Focus on skills, qualifications, and experience',
            'Ensure language is inclusive and welcoming to all candidates'
        ]

        high_severity_biases = [b for b in biases_found if b['severity'] == 'high']
        if high_severity_biases:
            recommendations.insert(0, 'HIGH PRIORITY: Address high-severity biases immediately')

        return recommendations

    def _check_inclusive_language(self, text: str) -> int:
        """Check for inclusive language usage (0-100 score)"""
        inclusive_terms = [
            'diverse', 'inclusive', 'equal opportunity', 'all backgrounds',
            'everyone', 'anyone', 'people', 'individuals', 'team members',
            'colleagues', 'professionals'
        ]

        score = 0
        text_lower = text.lower()

        for term in inclusive_terms:
            if term in text_lower:
                score += 15

        return min(score, 100)

_bias_detector_instance = None

def get_bias_detector() -> BiasDetector:
    """Get or create bias detector instance (singleton)"""
    global _bias_detector_instance
    if _bias_detector_instance is None:
        _bias_detector_instance = BiasDetector()
    return _bias_detector_instance
