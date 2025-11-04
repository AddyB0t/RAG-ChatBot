"""
Tests for Candidate Ranker
"""
import pytest
from app.services.candidate_ranker import CandidateRanker, get_candidate_ranker

class TestCandidateRanker:

    @pytest.fixture
    def ranker(self):
        return get_candidate_ranker()

    @pytest.fixture
    def sample_candidates(self):
        return [
            {
                "resume_id": "candidate1",
                "resume_data": {
                    "personal_info": {"full_name": "Alice Johnson"},
                    "experience": [
                        {"title": "Senior Engineer", "duration_years": 6}
                    ],
                    "education": [
                        {"degree": "Master of Science"}
                    ],
                    "skills": {
                        "technical": ["Python", "Java", "AWS", "Docker"],
                        "soft": ["Leadership", "Communication"]
                    },
                    "certifications": [
                        {"name": "AWS Certified"},
                        {"name": "Python Expert"}
                    ]
                },
                "match_data": {
                    "overall_score": 85,
                    "skill_analysis": {
                        "required_match_percentage": 90,
                        "preferred_match_percentage": 80
                    }
                },
                "availability": "immediate"
            },
            {
                "resume_id": "candidate2",
                "resume_data": {
                    "personal_info": {"full_name": "Bob Smith"},
                    "experience": [
                        {"title": "Software Engineer", "duration_years": 3}
                    ],
                    "education": [
                        {"degree": "Bachelor of Science"}
                    ],
                    "skills": {
                        "technical": ["Python", "JavaScript"],
                        "soft": ["Teamwork"]
                    },
                    "certifications": []
                },
                "match_data": {
                    "overall_score": 70,
                    "skill_analysis": {
                        "required_match_percentage": 70,
                        "preferred_match_percentage": 60
                    }
                },
                "availability": "within_1_month"
            },
            {
                "resume_id": "candidate3",
                "resume_data": {
                    "personal_info": {"full_name": "Carol Williams"},
                    "experience": [
                        {"title": "Lead Developer", "duration_years": 8}
                    ],
                    "education": [
                        {"degree": "PhD in Computer Science"}
                    ],
                    "skills": {
                        "technical": ["Python", "Java", "Kubernetes", "AWS", "React"],
                        "soft": ["Leadership", "Problem Solving", "Communication"]
                    },
                    "certifications": [
                        {"name": "AWS Certified"},
                        {"name": "Kubernetes Expert"},
                        {"name": "Scrum Master"}
                    ]
                },
                "match_data": {
                    "overall_score": 92,
                    "skill_analysis": {
                        "required_match_percentage": 95,
                        "preferred_match_percentage": 90
                    }
                },
                "availability": "within_2_weeks"
            }
        ]

    @pytest.fixture
    def sample_job_requirements(self):
        return {
            "job_title": "Senior Software Engineer",
            "required_skills": ["Python", "Java", "AWS"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "required_years": 5,
            "education_required": "Bachelor's degree in Computer Science"
        }

    def test_ranker_initialization(self, ranker):
        assert ranker is not None
        assert len(ranker.DEFAULT_WEIGHTS) == 7

    def test_default_weights_sum(self, ranker):
        total_weight = sum(ranker.DEFAULT_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.01

    def test_rank_candidates(self, ranker, sample_candidates, sample_job_requirements):
        result = ranker.rank_candidates(
            candidates=sample_candidates,
            job_requirements=sample_job_requirements
        )

        assert 'total_candidates' in result
        assert 'ranked_candidates' in result
        assert 'tier_distribution' in result
        assert 'statistics' in result
        assert result['total_candidates'] == 3

    def test_ranking_order(self, ranker, sample_candidates, sample_job_requirements):
        result = ranker.rank_candidates(
            candidates=sample_candidates,
            job_requirements=sample_job_requirements
        )

        candidates = result['ranked_candidates']
        assert candidates[0]['rank'] == 1
        assert candidates[1]['rank'] == 2
        assert candidates[2]['rank'] == 3

        assert candidates[0]['final_score'] >= candidates[1]['final_score']
        assert candidates[1]['final_score'] >= candidates[2]['final_score']

    def test_tier_distribution(self, ranker, sample_candidates, sample_job_requirements):
        result = ranker.rank_candidates(
            candidates=sample_candidates,
            job_requirements=sample_job_requirements
        )

        tier_dist = result['tier_distribution']
        assert 'S_tier' in tier_dist
        assert 'A_tier' in tier_dist
        assert 'B_tier' in tier_dist
        assert 'C_tier' in tier_dist
        assert 'D_tier' in tier_dist

        total_in_tiers = sum(tier_dist.values())
        assert total_in_tiers == 3

    def test_statistics(self, ranker, sample_candidates, sample_job_requirements):
        result = ranker.rank_candidates(
            candidates=sample_candidates,
            job_requirements=sample_job_requirements
        )

        stats = result['statistics']
        assert 'mean_score' in stats
        assert 'median_score' in stats
        assert 'std_deviation' in stats
        assert 'min_score' in stats
        assert 'max_score' in stats
        assert 'qualified_candidates' in stats

    def test_score_skills_match(self, ranker, sample_candidates, sample_job_requirements):
        candidate = sample_candidates[0]
        score = ranker._score_skills_match(
            candidate['resume_data'],
            sample_job_requirements,
            candidate['match_data']
        )

        assert score >= 0
        assert score <= 100

    def test_score_experience_match(self, ranker, sample_candidates, sample_job_requirements):
        candidate = sample_candidates[0]
        score = ranker._score_experience_match(
            candidate['resume_data'],
            sample_job_requirements
        )

        assert score >= 0
        assert score <= 100
        assert score >= 85

    def test_score_education_match(self, ranker, sample_candidates, sample_job_requirements):
        candidate = sample_candidates[0]
        score = ranker._score_education_match(
            candidate['resume_data'],
            sample_job_requirements
        )

        assert score >= 0
        assert score <= 100

    def test_score_cultural_fit(self, ranker, sample_candidates, sample_job_requirements):
        candidate = sample_candidates[0]
        score = ranker._score_cultural_fit(
            candidate['resume_data'],
            sample_job_requirements
        )

        assert score >= 0
        assert score <= 100

    def test_score_career_trajectory(self, ranker, sample_candidates):
        candidate = sample_candidates[0]
        score = ranker._score_career_trajectory(candidate['resume_data'])

        assert score >= 0
        assert score <= 100

    def test_score_certifications(self, ranker, sample_candidates):
        candidate_with_certs = sample_candidates[0]
        score1 = ranker._score_certifications(candidate_with_certs['resume_data'])
        assert score1 >= 55

        candidate_no_certs = sample_candidates[1]
        score2 = ranker._score_certifications(candidate_no_certs['resume_data'])
        assert score2 == 30

    def test_score_availability(self, ranker, sample_candidates):
        score_immediate = ranker._score_availability(sample_candidates[0])
        assert score_immediate == 100

        score_month = ranker._score_availability(sample_candidates[1])
        assert score_month == 80

    def test_custom_weights(self, ranker, sample_candidates, sample_job_requirements):
        custom_weights = {
            'skills_match': 0.50,
            'experience_match': 0.30,
            'education_match': 0.10,
            'cultural_fit': 0.05,
            'career_trajectory': 0.03,
            'certifications': 0.01,
            'availability': 0.01
        }

        result = ranker.rank_candidates(
            candidates=sample_candidates,
            job_requirements=sample_job_requirements,
            weights=custom_weights
        )

        assert result['weights_used'] == custom_weights

    def test_interview_priority(self, ranker):
        priority_urgent = ranker._determine_interview_priority(90, {'skills_match': 85})
        assert priority_urgent == 'urgent'

        priority_high = ranker._determine_interview_priority(75, {'skills_match': 75})
        assert priority_high == 'high'

        priority_medium = ranker._determine_interview_priority(60, {'skills_match': 60})
        assert priority_medium == 'medium'

        priority_low = ranker._determine_interview_priority(40, {'skills_match': 40})
        assert priority_low == 'low'

    def test_generate_recommendation(self, ranker):
        rec1 = ranker._generate_recommendation(90, ["Great skills"], [])
        assert "STRONG RECOMMEND" in rec1

        rec2 = ranker._generate_recommendation(75, ["Good skills"], [])
        assert "RECOMMEND" in rec2

        rec3 = ranker._generate_recommendation(60, [], ["Limited experience"])
        assert "CONSIDER" in rec3

        rec4 = ranker._generate_recommendation(30, [], ["Multiple gaps"])
        assert "NOT RECOMMENDED" in rec4

    def test_identify_strengths_weaknesses(self, ranker):
        scores = {
            'skills_match': 90,
            'experience_match': 85,
            'education_match': 80,
            'cultural_fit': 75,
            'career_trajectory': 70,
            'certifications': 55,
            'availability': 100
        }
        weights = ranker.DEFAULT_WEIGHTS

        strengths, weaknesses = ranker._identify_candidate_strengths_weaknesses(scores, weights)

        assert isinstance(strengths, list)
        assert isinstance(weaknesses, list)
        assert len(strengths) > 0

    def test_assign_tiers(self, ranker):
        candidates = [
            {'final_score': 95},
            {'final_score': 80},
            {'final_score': 65},
            {'final_score': 50},
            {'final_score': 35}
        ]

        tiers = ranker._assign_tiers(candidates)

        assert candidates[0]['tier'] == 'S'
        assert candidates[1]['tier'] == 'A'
        assert candidates[2]['tier'] == 'B'
        assert candidates[3]['tier'] == 'C'
        assert candidates[4]['tier'] == 'D'

    def test_compare_candidates(self, ranker):
        candidate1 = {
            'final_score': 85,
            'category_scores': {
                'skills_match': 90,
                'experience_match': 85
            }
        }

        candidate2 = {
            'final_score': 75,
            'category_scores': {
                'skills_match': 80,
                'experience_match': 70
            }
        }

        comparison = ranker.compare_candidates(candidate1, candidate2)

        assert 'candidate1_score' in comparison
        assert 'candidate2_score' in comparison
        assert 'score_difference' in comparison
        assert 'winner' in comparison
        assert 'category_comparison' in comparison
        assert comparison['winner'] == 'candidate1'

    def test_percentile_calculation(self, ranker, sample_candidates, sample_job_requirements):
        result = ranker.rank_candidates(
            candidates=sample_candidates,
            job_requirements=sample_job_requirements
        )

        for candidate in result['ranked_candidates']:
            assert 'percentile' in candidate
            assert candidate['percentile'] >= 0
            assert candidate['percentile'] <= 100

    def test_singleton_pattern(self):
        ranker1 = get_candidate_ranker()
        ranker2 = get_candidate_ranker()
        assert ranker1 is ranker2

    def test_single_candidate(self, ranker, sample_job_requirements):
        single_candidate = [{
            "resume_id": "candidate1",
            "resume_data": {
                "personal_info": {"full_name": "Test Candidate"},
                "experience": [{"duration_years": 5}],
                "education": [{"degree": "Bachelor"}],
                "skills": {"technical": ["Python"]},
                "certifications": []
            },
            "match_data": {"overall_score": 75},
            "availability": "immediate"
        }]

        result = ranker.rank_candidates(
            candidates=single_candidate,
            job_requirements=sample_job_requirements
        )

        assert result['total_candidates'] == 1
        assert result['ranked_candidates'][0]['rank'] == 1
        assert result['ranked_candidates'][0]['percentile'] == 100.0

    def test_empty_candidates_list(self, ranker, sample_job_requirements):
        result = ranker.rank_candidates(
            candidates=[],
            job_requirements=sample_job_requirements
        )

        assert result['total_candidates'] == 0
        assert len(result['ranked_candidates']) == 0

    def test_ranking_criteria_list(self, ranker, sample_candidates, sample_job_requirements):
        result = ranker.rank_candidates(
            candidates=sample_candidates,
            job_requirements=sample_job_requirements
        )

        assert 'ranking_criteria' in result
        assert len(result['ranking_criteria']) == 7
