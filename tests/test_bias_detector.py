"""
Tests for Bias Detector
"""
import pytest
from app.services.bias_detector import BiasDetector, get_bias_detector

class TestBiasDetector:

    @pytest.fixture
    def detector(self):
        return get_bias_detector()

    @pytest.fixture
    def sample_resume_with_bias(self):
        return {
            "personal_info": {
                "full_name": "John Smith",
                "summary": "He is an experienced developer who recently graduated"
            },
            "experience": [
                {
                    "title": "Senior Developer",
                    "company": "Tech Corp",
                    "description": "He led a team of young developers"
                }
            ],
            "education": [
                {
                    "institution": "Prestigious University",
                    "degree": "Bachelor of Science",
                    "field": "Computer Science"
                }
            ],
            "skills": {
                "technical": ["Python", "Java"],
                "soft": ["leadership"]
            }
        }

    @pytest.fixture
    def sample_resume_no_bias(self):
        return {
            "personal_info": {
                "full_name": "Alex Johnson",
                "summary": "Experienced developer with strong technical skills"
            },
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Solutions",
                    "description": "Developed applications and collaborated with team"
                }
            ],
            "education": [
                {
                    "institution": "State University",
                    "degree": "Bachelor of Science",
                    "field": "Computer Science"
                }
            ],
            "skills": {
                "technical": ["Python", "JavaScript"],
                "soft": ["teamwork", "communication"]
            }
        }

    def test_detector_initialization(self, detector):
        assert detector is not None
        assert len(detector.GENDER_INDICATORS) == 3
        assert 'male' in detector.GENDER_INDICATORS
        assert 'female' in detector.GENDER_INDICATORS
        assert 'neutral' in detector.GENDER_INDICATORS

    def test_bias_patterns_compiled(self, detector):
        assert len(detector.bias_patterns) == 7
        assert 'gender' in detector.bias_patterns
        assert 'age' in detector.bias_patterns
        assert 'cultural' in detector.bias_patterns
        assert 'disability' in detector.bias_patterns

    def test_detect_gender_bias(self, detector, sample_resume_with_bias):
        result = detector.detect_bias_in_resume(sample_resume_with_bias)

        assert 'has_bias' in result
        assert result['has_bias'] is True
        assert result['bias_score'] > 0

        gender_biases = [b for b in result['biases_detected'] if b['category'] == 'gender']
        assert len(gender_biases) > 0
        assert 'he' in str(gender_biases[0]['matches']).lower()

    def test_detect_age_bias(self, detector, sample_resume_with_bias):
        result = detector.detect_bias_in_resume(sample_resume_with_bias)

        age_biases = [b for b in result['biases_detected'] if b['category'] == 'age']
        assert len(age_biases) > 0

    def test_detect_socioeconomic_bias(self, detector, sample_resume_with_bias):
        result = detector.detect_bias_in_resume(sample_resume_with_bias)

        socio_biases = [b for b in result['biases_detected'] if b['category'] == 'socioeconomic']
        assert len(socio_biases) > 0

    def test_no_bias_resume(self, detector, sample_resume_no_bias):
        result = detector.detect_bias_in_resume(sample_resume_no_bias)

        assert 'has_bias' in result
        assert result['bias_score'] >= 0

    def test_bias_severity_calculation(self, detector):
        severity_low = detector._calculate_severity('gender', 1)
        severity_medium = detector._calculate_severity('gender', 2)
        severity_high = detector._calculate_severity('gender', 3)

        assert severity_low == 'low'
        assert severity_medium == 'medium'
        assert severity_high == 'high'

    def test_overall_risk_calculation(self, detector):
        biases_high = [
            {'severity': 'high', 'count': 5},
            {'severity': 'high', 'count': 3}
        ]
        risk = detector._calculate_overall_risk(50, biases_high)
        assert risk == 'high'

        biases_low = [{'severity': 'low', 'count': 1}]
        risk = detector._calculate_overall_risk(10, biases_low)
        assert risk == 'low'

    def test_job_description_bias_detection(self, detector):
        job_desc_biased = "We need a young, energetic guy to join our team. He should be a recent graduate."
        result = detector.detect_bias_in_job_description(job_desc_biased)

        assert result['has_bias'] is True
        assert result['bias_score'] > 0
        assert len(result['biases_detected']) > 0
        assert 'inclusive_language_score' in result

    def test_inclusive_language_scoring(self, detector):
        job_desc_inclusive = "We welcome diverse candidates from all backgrounds. Everyone is encouraged to apply."
        result = detector.detect_bias_in_job_description(job_desc_inclusive)

        assert result['inclusive_language_score'] > 0

    def test_recommendations_generated(self, detector, sample_resume_with_bias):
        result = detector.detect_bias_in_resume(sample_resume_with_bias)

        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
        assert isinstance(result['recommendations'], list)

    def test_categories_affected(self, detector, sample_resume_with_bias):
        result = detector.detect_bias_in_resume(sample_resume_with_bias)

        assert 'categories_affected' in result
        assert isinstance(result['categories_affected'], list)
        assert 'gender' in result['categories_affected']

    def test_bias_description(self, detector):
        desc_gender = detector._get_bias_description('gender')
        assert 'gender' in desc_gender.lower()

        desc_age = detector._get_bias_description('age')
        assert 'age' in desc_age.lower()

    def test_bias_recommendation(self, detector):
        rec_gender = detector._get_bias_recommendation('gender')
        assert len(rec_gender) > 0
        assert 'neutral' in rec_gender.lower()

    def test_singleton_pattern(self):
        detector1 = get_bias_detector()
        detector2 = get_bias_detector()
        assert detector1 is detector2

    def test_empty_resume_data(self, detector):
        empty_resume = {}
        result = detector.detect_bias_in_resume(empty_resume)

        assert 'has_bias' in result
        assert result['bias_score'] >= 0

    def test_analyzed_at_timestamp(self, detector, sample_resume_no_bias):
        result = detector.detect_bias_in_resume(sample_resume_no_bias)

        assert 'analyzed_at' in result
        assert result['analyzed_at'] is not None
