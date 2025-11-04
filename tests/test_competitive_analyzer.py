"""
Tests for Competitive Analyzer
"""
import pytest
from app.services.competitive_analyzer import CompetitiveAnalyzer, get_competitive_analyzer

class TestCompetitiveAnalyzer:

    @pytest.fixture
    def analyzer(self):
        return get_competitive_analyzer()

    @pytest.fixture
    def sample_resume_strong(self):
        return {
            "personal_info": {
                "full_name": "Senior Developer"
            },
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "duration_years": 5
                },
                {
                    "title": "Software Engineer",
                    "company": "StartUp Inc",
                    "duration_years": 3
                }
            ],
            "education": [
                {
                    "degree": "Master of Science",
                    "institution": "University",
                    "field": "Computer Science"
                }
            ],
            "skills": {
                "technical": ["Python", "Java", "JavaScript", "AWS", "Docker", "Kubernetes"],
                "soft": ["Communication", "Leadership", "Teamwork"],
                "languages": ["English", "Spanish"]
            },
            "certifications": [
                {"name": "AWS Certified"},
                {"name": "Python Expert"},
                {"name": "Kubernetes Admin"}
            ]
        }

    @pytest.fixture
    def sample_job_requirements(self):
        return {
            "job_title": "Senior Software Engineer",
            "description": "Looking for experienced software engineer",
            "required_skills": ["Python", "JavaScript", "AWS", "Docker"],
            "preferred_skills": ["Kubernetes", "React"],
            "required_years": 5,
            "education_required": "Bachelor's degree"
        }

    def test_analyzer_initialization(self, analyzer):
        assert analyzer is not None
        assert len(analyzer.INDUSTRY_BENCHMARKS) == 5

    def test_industry_benchmarks(self, analyzer):
        assert 'software_engineering' in analyzer.INDUSTRY_BENCHMARKS
        assert 'data_science' in analyzer.INDUSTRY_BENCHMARKS
        assert 'product_management' in analyzer.INDUSTRY_BENCHMARKS
        assert 'devops' in analyzer.INDUSTRY_BENCHMARKS
        assert 'default' in analyzer.INDUSTRY_BENCHMARKS

    def test_infer_industry_software(self, analyzer):
        job_req = {
            "job_title": "Software Engineer",
            "description": "Python developer needed",
            "required_skills": ["python", "java"]
        }
        industry = analyzer._infer_industry(job_req)
        assert industry == 'software_engineering'

    def test_infer_industry_data_science(self, analyzer):
        job_req = {
            "job_title": "Data Scientist",
            "description": "Machine learning expert",
            "required_skills": ["python", "machine learning"]
        }
        industry = analyzer._infer_industry(job_req)
        assert industry == 'data_science'

    def test_infer_industry_product_management(self, analyzer):
        job_req = {
            "job_title": "Product Manager",
            "description": "Product owner needed",
            "required_skills": ["agile", "roadmap"]
        }
        industry = analyzer._infer_industry(job_req)
        assert industry == 'product_management'

    def test_analyze_competitiveness(self, analyzer, sample_resume_strong, sample_job_requirements):
        result = analyzer.analyze_competitiveness(
            resume_data=sample_resume_strong,
            job_requirements=sample_job_requirements,
            match_score=85.0
        )

        assert 'competitive_score' in result
        assert 'market_position' in result
        assert 'industry_benchmark' in result
        assert result['competitive_score'] >= 0
        assert result['competitive_score'] <= 100

    def test_experience_competitiveness(self, analyzer, sample_resume_strong):
        benchmarks = analyzer.INDUSTRY_BENCHMARKS['software_engineering']
        result = analyzer._analyze_experience_competitiveness(
            sample_resume_strong,
            benchmarks
        )

        assert 'total_years' in result
        assert 'benchmark_years' in result
        assert 'competitiveness_level' in result
        assert 'score' in result
        assert result['total_years'] == 8.0
        assert result['competitiveness_level'] in ['highly_competitive', 'competitive', 'moderately_competitive', 'below_average']

    def test_skills_competitiveness(self, analyzer, sample_resume_strong, sample_job_requirements):
        benchmarks = analyzer.INDUSTRY_BENCHMARKS['software_engineering']
        result = analyzer._analyze_skills_competitiveness(
            sample_resume_strong,
            sample_job_requirements,
            benchmarks
        )

        assert 'total_skills' in result
        assert 'industry_coverage' in result
        assert 'job_coverage' in result
        assert 'competitiveness_level' in result
        assert 'score' in result
        assert result['total_skills'] > 0
        assert result['job_coverage'] >= 0

    def test_education_competitiveness(self, analyzer, sample_resume_strong):
        benchmarks = analyzer.INDUSTRY_BENCHMARKS['software_engineering']
        result = analyzer._analyze_education_competitiveness(
            sample_resume_strong,
            benchmarks
        )

        assert 'highest_degree' in result
        assert 'degree_level' in result
        assert 'preferred_level' in result
        assert 'competitiveness_level' in result
        assert 'score' in result
        assert result['degree_level'] == 4

    def test_calculate_market_position(self, analyzer):
        experience_comp = {'score': 90}
        skills_comp = {'score': 85}
        education_comp = {'score': 80}

        result = analyzer._calculate_market_position(
            match_score=85.0,
            experience_comp=experience_comp,
            skills_comp=skills_comp,
            education_comp=education_comp
        )

        assert 'score' in result
        assert 'position' in result
        assert 'description' in result
        assert 'percentile' in result
        assert result['position'] in ['top_tier', 'strong', 'average', 'below_average']

    def test_score_to_percentile(self, analyzer):
        percentile_95 = analyzer._score_to_percentile(95)
        assert percentile_95 == 99

        percentile_85 = analyzer._score_to_percentile(85)
        assert percentile_85 == 90

        percentile_55 = analyzer._score_to_percentile(55)
        assert percentile_55 == 50

    def test_identify_strengths_weaknesses(self, analyzer):
        experience_comp = {'score': 95, 'total_years': 8, 'gap_years': 0}
        skills_comp = {'score': 87, 'job_coverage': 90, 'missing_job_skills': []}
        education_comp = {'score': 80, 'highest_degree': 'Master'}

        result = analyzer._identify_strengths_weaknesses(
            experience_comp,
            skills_comp,
            education_comp
        )

        assert 'strengths' in result
        assert 'weaknesses' in result
        assert isinstance(result['strengths'], list)
        assert isinstance(result['weaknesses'], list)
        assert len(result['strengths']) > 0

    def test_identify_competitive_advantages(self, analyzer, sample_resume_strong, sample_job_requirements):
        benchmarks = analyzer.INDUSTRY_BENCHMARKS['software_engineering']
        result = analyzer._identify_competitive_advantages(
            sample_resume_strong,
            sample_job_requirements,
            benchmarks
        )

        assert isinstance(result, list)
        assert len(result) > 0
        for advantage in result:
            assert 'advantage' in advantage
            assert 'description' in advantage
            assert 'impact' in advantage

    def test_generate_improvement_priorities(self, analyzer):
        weaknesses = ["Limited experience (2 years gap)", "Skill gaps (3 key skills missing)"]
        benchmarks = analyzer.INDUSTRY_BENCHMARKS['software_engineering']

        result = analyzer._generate_improvement_priorities(weaknesses, benchmarks)

        assert isinstance(result, list)
        assert len(result) > 0
        for priority in result:
            assert 'priority' in priority
            assert 'area' in priority
            assert 'action' in priority
            assert 'timeline' in priority

    def test_compare_with_candidates(self, analyzer, sample_resume_strong):
        other_candidates = [
            {'match_score': 75},
            {'match_score': 80},
            {'match_score': 70}
        ]

        result = analyzer._compare_with_candidates(
            sample_resume_strong,
            match_score=85.0,
            other_candidates=other_candidates
        )

        assert 'rank' in result
        assert 'total_candidates' in result
        assert 'percentile' in result
        assert 'tier' in result
        assert result['rank'] == 1
        assert result['total_candidates'] == 4

    def test_generate_market_insights(self, analyzer):
        market_position = {
            'position': 'top_tier',
            'score': 90
        }
        industry = 'software_engineering'
        benchmarks = analyzer.INDUSTRY_BENCHMARKS['software_engineering']

        result = analyzer._generate_market_insights(market_position, industry, benchmarks)

        assert isinstance(result, list)
        assert len(result) > 0
        assert any('competitive' in insight.lower() for insight in result)

    def test_salary_range_in_benchmarks(self, analyzer):
        for industry, benchmark in analyzer.INDUSTRY_BENCHMARKS.items():
            assert 'avg_salary_range' in benchmark
            assert isinstance(benchmark['avg_salary_range'], tuple)
            assert len(benchmark['avg_salary_range']) == 2

    def test_analyzed_at_timestamp(self, analyzer, sample_resume_strong, sample_job_requirements):
        result = analyzer.analyze_competitiveness(
            resume_data=sample_resume_strong,
            job_requirements=sample_job_requirements,
            match_score=85.0
        )

        assert 'analyzed_at' in result
        assert result['analyzed_at'] is not None

    def test_singleton_pattern(self):
        analyzer1 = get_competitive_analyzer()
        analyzer2 = get_competitive_analyzer()
        assert analyzer1 is analyzer2

    def test_weak_candidate(self, analyzer, sample_job_requirements):
        weak_resume = {
            "experience": [{"duration_years": 1}],
            "education": [{"degree": "High School"}],
            "skills": {"technical": ["HTML"]},
            "certifications": []
        }

        result = analyzer.analyze_competitiveness(
            resume_data=weak_resume,
            job_requirements=sample_job_requirements,
            match_score=40.0
        )

        assert result['competitive_score'] < 60
        assert result['market_position'] in ['average', 'below_average']

    def test_empty_experience(self, analyzer):
        resume_no_exp = {
            "experience": [],
            "education": [],
            "skills": {},
            "certifications": []
        }

        benchmarks = analyzer.INDUSTRY_BENCHMARKS['default']
        result = analyzer._analyze_experience_competitiveness(resume_no_exp, benchmarks)

        assert result['total_years'] == 0
        assert result['competitiveness_level'] == 'below_average'
