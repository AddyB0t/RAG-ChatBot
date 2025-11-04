"""
Pytest configuration and fixtures for API testing
"""
import pytest
import os
import sys
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.core.database import Base, get_db
from app.models.database import Resume, ResumeJobMatch, AIAnalysis, ResumeParserErrorLog

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers() -> dict:
    """Return authentication headers"""
    return {"Authorization": "Bearer QWERTY"}

@pytest.fixture
def sample_resume_data() -> dict:
    """Sample structured resume data for testing"""
    return {
        "name": {
            "full_name": "John Doe",
            "first_name": "John",
            "last_name": "Doe"
        },
        "contact": {
            "email": "john.doe@example.com",
            "phone": "+1-555-123-4567",
            "linkedin": "https://linkedin.com/in/johndoe",
            "address": {
                "city": "San Francisco",
                "state": "CA",
                "country": "USA"
            }
        },
        "summary": "Experienced software engineer with 5+ years in backend development",
        "experience": [
            {
                "job_title": "Senior Software Engineer",
                "company_name": "Tech Corp",
                "location": "San Francisco, CA",
                "start_date": "2021-03-01",
                "end_date": "2025-09-01",
                "is_current": True,
                "duration": "4 years 6 months",
                "description": "Led development of microservices architecture",
                "achievements": [
                    "Improved system performance by 40%",
                    "Led team of 5 developers"
                ],
                "technologies": ["Python", "Docker", "AWS", "PostgreSQL"]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "institution": "University of California, Berkeley",
                "location": "Berkeley, CA",
                "graduation_date": "2018-05-15",
                "gpa": 3.7
            }
        ],
        "skills": {
            "technical_skills": ["Python", "JavaScript", "Docker", "AWS"],
            "soft_skills": ["Leadership", "Communication", "Problem Solving"],
            "languages": ["English", "Spanish"]
        },
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "issuer": "Amazon Web Services",
                "issue_date": "2023-06-15",
                "expiry_date": "2026-06-15"
            }
        ]
    }

@pytest.fixture
def sample_job_description() -> dict:
    """Sample job description for testing"""
    return {
        "job_title": "Senior Software Engineer",
        "company_name": "Tech Innovation Corp",
        "job_description": "We are seeking a highly skilled Senior Software Engineer to join our team. Must have experience with Python, AWS, and microservices.",
        "required_skills": ["Python", "AWS", "Microservices"],
        "preferred_skills": ["Docker", "PostgreSQL"]
    }

