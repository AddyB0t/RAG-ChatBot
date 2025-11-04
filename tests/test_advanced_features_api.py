"""
Integration Tests for Advanced Features API
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import uuid

class TestAdvancedFeaturesAPI:

    @pytest.fixture
    def client(self):
        from app.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        with patch('app.core.security.verify_password', return_value=True):
            yield

    @pytest.fixture
    def mock_resume_id(self):
        return str(uuid.uuid4())

    @pytest.fixture
    def sample_resume_data(self):
        return {
            "personal_info": {
                "full_name": "John Smith",
                "contact": {
                    "email": "john@example.com"
                }
            },
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp"
                }
            ],
            "education": [],
            "skills": {"technical": ["Python", "Java"]},
            "certifications": []
        }

    def test_bias_detection_endpoint_exists(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    @patch('app.api.routes.advanced_features.get_db')
    @patch('app.api.routes.advanced_features.get_bias_detector')
    def test_bias_detection_success(self, mock_detector, mock_db, client, mock_auth, mock_resume_id, sample_resume_data):
        mock_resume = Mock()
        mock_resume.id = uuid.UUID(mock_resume_id)
        mock_resume.structured_data = sample_resume_data

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_resume
        mock_db.return_value = mock_session

        detector_instance = Mock()
        detector_instance.detect_bias_in_resume.return_value = {
            "has_bias": True,
            "bias_score": 35.0,
            "overall_risk": "medium",
            "biases_detected": [
                {
                    "category": "gender",
                    "severity": "medium",
                    "matches": ["he"],
                    "count": 1,
                    "description": "Gender bias",
                    "recommendation": "Use neutral language"
                }
            ],
            "total_bias_indicators": 1,
            "categories_affected": ["gender"],
            "recommendations": ["Use neutral language"],
            "analyzed_at": "2025-11-04T00:00:00"
        }
        mock_detector.return_value = detector_instance

        response = client.post(
            f"/api/v1/advanced/bias-detection/{mock_resume_id}",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["has_bias"] is True
        assert data["bias_score"] == 35.0

    @patch('app.api.routes.advanced_features.get_db')
    def test_bias_detection_resume_not_found(self, mock_db, client, mock_auth, mock_resume_id):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value = mock_session

        response = client.post(
            f"/api/v1/advanced/bias-detection/{mock_resume_id}",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 404

    @patch('app.api.routes.advanced_features.get_db')
    @patch('app.api.routes.advanced_features.get_anonymizer')
    def test_anonymization_success(self, mock_anonymizer, mock_db, client, mock_auth, mock_resume_id, sample_resume_data):
        mock_resume = Mock()
        mock_resume.id = uuid.UUID(mock_resume_id)
        mock_resume.structured_data = sample_resume_data

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_resume
        mock_db.return_value = mock_session

        anonymizer_instance = Mock()
        anonymized_data = sample_resume_data.copy()
        anonymized_data["personal_info"]["full_name"] = "Candidate ABC123"
        anonymizer_instance.anonymize_resume.return_value = anonymized_data
        anonymizer_instance.get_anonymization_report.return_value = {
            "fields_removed": ["name", "contact"],
            "fields_masked": [],
            "fields_preserved": ["skills"],
            "anonymization_level": "high"
        }
        mock_anonymizer.return_value = anonymizer_instance

        response = client.post(
            "/api/v1/advanced/anonymize",
            json={"resume_id": mock_resume_id},
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "anonymized_data" in data

    @patch('app.api.routes.advanced_features.get_db')
    @patch('app.api.routes.advanced_features.get_competitive_analyzer')
    @patch('app.services.job_matcher.matcher_manager.get_job_matcher')
    def test_competitive_analysis_success(self, mock_matcher, mock_analyzer, mock_db, client, mock_auth, mock_resume_id, sample_resume_data):
        mock_resume = Mock()
        mock_resume.id = uuid.UUID(mock_resume_id)
        mock_resume.structured_data = sample_resume_data

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_resume
        mock_db.return_value = mock_session

        matcher_instance = Mock()
        matcher_instance.match_resume_to_job.return_value = {
            "overall_score": 85,
            "job_requirements": {}
        }
        mock_matcher.return_value = matcher_instance

        analyzer_instance = Mock()
        analyzer_instance.analyze_competitiveness.return_value = {
            "competitive_score": 82.5,
            "market_position": {"position": "strong"},
            "industry_benchmark": "software_engineering",
            "experience_analysis": {},
            "skills_analysis": {},
            "education_analysis": {},
            "strengths": ["Strong experience"],
            "weaknesses": [],
            "competitive_advantages": [],
            "improvement_priorities": [],
            "market_insights": []
        }
        mock_analyzer.return_value = analyzer_instance

        response = client.post(
            "/api/v1/advanced/competitive-analysis",
            json={
                "resume_id": mock_resume_id,
                "job_description": "Software engineer needed",
                "job_title": "Senior Software Engineer"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "competitive_score" in data

    @patch('app.api.routes.advanced_features.get_db')
    @patch('app.api.routes.advanced_features.get_candidate_ranker')
    @patch('app.services.job_matcher.matcher_manager.get_job_matcher')
    @patch('app.services.job_matcher.job_parser.JobDescriptionParser')
    def test_rank_candidates_success(self, mock_parser, mock_matcher, mock_ranker, mock_db, client, mock_auth, sample_resume_data):
        resume_id1 = str(uuid.uuid4())
        resume_id2 = str(uuid.uuid4())

        mock_resume1 = Mock()
        mock_resume1.id = uuid.UUID(resume_id1)
        mock_resume1.structured_data = sample_resume_data

        mock_resume2 = Mock()
        mock_resume2.id = uuid.UUID(resume_id2)
        mock_resume2.structured_data = sample_resume_data

        def mock_query_filter(filter_expr):
            mock_result = Mock()
            if str(resume_id1) in str(filter_expr):
                mock_result.first.return_value = mock_resume1
            else:
                mock_result.first.return_value = mock_resume2
            return mock_result

        mock_session = MagicMock()
        mock_session.query.return_value.filter.side_effect = mock_query_filter
        mock_db.return_value = mock_session

        matcher_instance = Mock()
        matcher_instance.match_resume_to_job.return_value = {
            "overall_score": 85,
            "job_requirements": {}
        }
        mock_matcher.return_value = matcher_instance

        parser_instance = Mock()
        parser_instance.parse_job_description.return_value = {}
        mock_parser.return_value = parser_instance

        ranker_instance = Mock()
        ranker_instance.rank_candidates.return_value = {
            "total_candidates": 2,
            "ranked_candidates": [
                {
                    "rank": 1,
                    "final_score": 87.5,
                    "tier": "A"
                },
                {
                    "rank": 2,
                    "final_score": 75.0,
                    "tier": "B"
                }
            ],
            "tier_distribution": {"A_tier": 1, "B_tier": 1},
            "statistics": {},
            "weights_used": {},
            "ranking_criteria": []
        }
        mock_ranker.return_value = ranker_instance

        response = client.post(
            "/api/v1/advanced/rank-candidates",
            json={
                "resume_ids": [resume_id1, resume_id2],
                "job_description": "Software engineer needed",
                "job_title": "Senior Software Engineer"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_candidates"] == 2

    @patch('app.api.routes.advanced_features.get_bias_detector')
    def test_job_description_bias_detection(self, mock_detector, client, mock_auth):
        detector_instance = Mock()
        detector_instance.detect_bias_in_job_description.return_value = {
            "has_bias": False,
            "bias_score": 10.0,
            "overall_risk": "low",
            "biases_detected": [],
            "total_bias_indicators": 0,
            "categories_affected": [],
            "inclusive_language_score": 80,
            "recommendations": [],
            "analyzed_at": "2025-11-04T00:00:00"
        }
        mock_detector.return_value = detector_instance

        response = client.get(
            "/api/v1/advanced/bias-detection/job-description",
            params={"job_description": "We need a skilled developer"},
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "inclusive_language_score" in data

    @patch('app.api.routes.advanced_features.get_db')
    @patch('app.api.routes.advanced_features.get_candidate_ranker')
    def test_candidate_comparison(self, mock_ranker, mock_db, client, mock_auth):
        candidate1_id = str(uuid.uuid4())
        candidate2_id = str(uuid.uuid4())

        mock_match1 = Mock()
        mock_match1.resume_id = uuid.UUID(candidate1_id)
        mock_match1.overall_score = 85
        mock_match1.category_scores = {"skills": 90}

        mock_match2 = Mock()
        mock_match2.resume_id = uuid.UUID(candidate2_id)
        mock_match2.overall_score = 75
        mock_match2.category_scores = {"skills": 80}

        def mock_query_filter(filter_expr):
            mock_result = Mock()
            if str(candidate1_id) in str(filter_expr):
                mock_result.first.return_value = mock_match1
            else:
                mock_result.first.return_value = mock_match2
            return mock_result

        mock_session = MagicMock()
        mock_session.query.return_value.filter.side_effect = mock_query_filter
        mock_db.return_value = mock_session

        ranker_instance = Mock()
        ranker_instance.compare_candidates.return_value = {
            "candidate1_score": 85,
            "candidate2_score": 75,
            "score_difference": 10,
            "winner": "candidate1",
            "category_comparison": {}
        }
        mock_ranker.return_value = ranker_instance

        response = client.post(
            "/api/v1/advanced/candidate-comparison",
            params={
                "candidate1_id": candidate1_id,
                "candidate2_id": candidate2_id
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["winner"] == "candidate1"

    def test_unauthorized_access(self, client):
        resume_id = str(uuid.uuid4())
        response = client.post(f"/api/v1/advanced/bias-detection/{resume_id}")

        assert response.status_code in [401, 403]

    @patch('app.api.routes.advanced_features.get_db')
    def test_anonymization_with_custom_options(self, mock_db, client, mock_auth, mock_resume_id, sample_resume_data):
        mock_resume = Mock()
        mock_resume.id = uuid.UUID(mock_resume_id)
        mock_resume.structured_data = sample_resume_data

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_resume
        mock_db.return_value = mock_session

        with patch('app.api.routes.advanced_features.get_anonymizer') as mock_anonymizer:
            anonymizer_instance = Mock()
            anonymizer_instance.anonymize_resume.return_value = sample_resume_data.copy()
            anonymizer_instance.get_anonymization_report.return_value = {
                "fields_removed": [],
                "fields_masked": [],
                "fields_preserved": [],
                "anonymization_level": "low"
            }
            mock_anonymizer.return_value = anonymizer_instance

            response = client.post(
                "/api/v1/advanced/anonymize",
                json={
                    "resume_id": mock_resume_id,
                    "options": {
                        "remove_name": True,
                        "remove_contact": False
                    }
                },
                headers={"Authorization": "Bearer test-token"}
            )

            assert response.status_code == 200

    @patch('app.api.routes.advanced_features.get_db')
    def test_rank_candidates_no_valid_resumes(self, mock_db, client, mock_auth):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value = mock_session

        response = client.post(
            "/api/v1/advanced/rank-candidates",
            json={
                "resume_ids": [str(uuid.uuid4())],
                "job_description": "Test job",
                "job_title": "Test Title"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 400
