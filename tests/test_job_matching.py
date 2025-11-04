"""
Test job matching endpoints
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.database import Resume, ResumeJobMatch

def test_job_match_resume_not_found(client: TestClient, auth_headers: dict):
    """Test job matching with non-existent resume"""
    match_request = {
        "resume_id": str(uuid.uuid4()),
        "job_title": "Software Engineer",
        "job_description": "Looking for a skilled developer",
        "company_name": "Test Corp"
    }
    response = client.post("/api/v1/jobs/match", headers=auth_headers, json=match_request)
    assert response.status_code == 404

def test_job_match_incomplete_resume(client: TestClient, auth_headers: dict, db_session: Session):
    """Test job matching with resume that hasn't been processed"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test.pdf",
        file_path="/fake/path/test.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="hash123",
        status="pending",
        structured_data=None
    )
    db_session.add(resume)
    db_session.commit()

    match_request = {
        "resume_id": str(resume.id),
        "job_title": "Software Engineer",
        "job_description": "Looking for a skilled developer"
    }
    response = client.post("/api/v1/jobs/match", headers=auth_headers, json=match_request)
    assert response.status_code == 400
    assert "not yet processed" in response.json()["detail"].lower()

def test_job_match_missing_required_fields(client: TestClient, auth_headers: dict):
    """Test job matching with missing required fields"""
    incomplete_request = {
        "resume_id": str(uuid.uuid4())
    }
    response = client.post("/api/v1/jobs/match", headers=auth_headers, json=incomplete_request)
    assert response.status_code == 422

def test_get_match_details_not_found(client: TestClient, auth_headers: dict):
    """Test getting non-existent match details"""
    fake_match_id = uuid.uuid4()
    response = client.get(f"/api/v1/jobs/matches/{fake_match_id}", headers=auth_headers)
    assert response.status_code == 404

def test_get_resume_matches_empty(client: TestClient, auth_headers: dict, db_session: Session):
    """Test getting matches for resume with no matches"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test.pdf",
        file_path="/fake/path/test.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="hash456",
        status="completed",
        structured_data={"name": {"full_name": "Test User"}}
    )
    db_session.add(resume)
    db_session.commit()

    response = client.get(f"/api/v1/jobs/resumes/{resume.id}/matches", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_create_and_get_job_match(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test creating a job match and retrieving it"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test.pdf",
        file_path="/fake/path/test.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="hash789",
        status="completed",
        structured_data=sample_resume_data
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)

    job_match = ResumeJobMatch(
        id=uuid.uuid4(),
        resume_id=resume.id,
        job_title="Senior Software Engineer",
        company_name="Tech Corp",
        job_description="We need a skilled engineer",
        overall_score=85,
        confidence_score=0.92,
        recommendation="Strong Match",
        category_scores={"skills": 90, "experience": 80},
        strength_areas=["Strong technical skills"],
        gap_analysis={"critical_gaps": []}
    )
    db_session.add(job_match)
    db_session.commit()
    db_session.refresh(job_match)

    response = client.get(f"/api/v1/jobs/matches/{job_match.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["overall_score"] == 85
    assert data["job_title"] == "Senior Software Engineer"
    assert data["recommendation"] == "Strong Match"

def test_list_resume_matches(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test listing all matches for a resume"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test.pdf",
        file_path="/fake/path/test.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="hash999",
        status="completed",
        structured_data=sample_resume_data
    )
    db_session.add(resume)
    db_session.commit()

    for i in range(3):
        job_match = ResumeJobMatch(
            id=uuid.uuid4(),
            resume_id=resume.id,
            job_title=f"Position {i}",
            job_description=f"Job {i}",
            overall_score=80 + i,
            confidence_score=0.85,
            recommendation="Good Match"
        )
        db_session.add(job_match)

    db_session.commit()

    response = client.get(f"/api/v1/jobs/resumes/{resume.id}/matches", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(match["resume_id"] == str(resume.id) for match in data)

def test_delete_job_match(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test deleting a job match"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test.pdf",
        file_path="/fake/path/test.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="hash111",
        status="completed",
        structured_data=sample_resume_data
    )
    db_session.add(resume)
    db_session.commit()

    job_match = ResumeJobMatch(
        id=uuid.uuid4(),
        resume_id=resume.id,
        job_title="Test Position",
        job_description="Test job",
        overall_score=75,
        confidence_score=0.80,
        recommendation="Moderate Match"
    )
    db_session.add(job_match)
    db_session.commit()
    match_id = job_match.id

    response = client.delete(f"/api/v1/jobs/matches/{match_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/api/v1/jobs/matches/{match_id}", headers=auth_headers)
    assert response.status_code == 404

def test_job_match_validation(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test job match request validation"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test.pdf",
        file_path="/fake/path/test.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="hash222",
        status="completed",
        structured_data=sample_resume_data
    )
    db_session.add(resume)
    db_session.commit()

    match_request = {
        "resume_id": str(resume.id),
        "job_title": "Software Engineer",
        "job_description": ""
    }
    response = client.post("/api/v1/jobs/match", headers=auth_headers, json=match_request)
    assert response.status_code in [400, 422, 500]

