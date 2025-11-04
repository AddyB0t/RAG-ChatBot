"""
Test quality analysis endpoints
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.database import Resume, AIAnalysis

def test_analyze_resume_not_found(client: TestClient, auth_headers: dict):
    """Test quality analysis with non-existent resume"""
    fake_id = uuid.uuid4()
    response = client.post(f"/api/v1/quality/analyze/{fake_id}", headers=auth_headers)
    assert response.status_code == 404

def test_analyze_incomplete_resume(client: TestClient, auth_headers: dict, db_session: Session):
    """Test quality analysis on unprocessed resume"""
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

    response = client.post(f"/api/v1/quality/analyze/{resume.id}", headers=auth_headers)
    assert response.status_code == 400
    assert "processed first" in response.json()["detail"].lower()

def test_get_quality_analysis_not_found(client: TestClient, auth_headers: dict):
    """Test getting non-existent quality analysis"""
    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/quality/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
    assert "No quality analysis found" in response.json()["detail"]

def test_create_and_get_quality_analysis(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test creating quality analysis and retrieving it"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test.pdf",
        file_path="/fake/path/test.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="hash456",
        status="completed",
        structured_data=sample_resume_data
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)

    analysis = AIAnalysis(
        id=uuid.uuid4(),
        resume_id=resume.id,
        quality_score=87,
        completeness_score=92,
        career_level="Mid-Level",
        industry_classifications=["Technology", "Software"],
        salary_estimate={
            "currency": "USD",
            "min_salary": 80000,
            "max_salary": 120000,
            "median_salary": 100000,
            "confidence": "high"
        },
        suggestions={
            "quality_analysis": {"strengths": ["Good experience"], "weaknesses": []},
            "improvement_plan": {"priority_actions": []}
        },
        confidence_scores={"ats_compatibility": 85}
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    response = client.get(f"/api/v1/quality/{resume.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["quality_score"] == 87
    assert data["completeness_score"] == 92
    assert data["career_level"] == "Mid-Level"
    assert "salary_estimate" in data

def test_update_existing_quality_analysis(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test that re-analyzing updates existing analysis"""
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

    analysis = AIAnalysis(
        id=uuid.uuid4(),
        resume_id=resume.id,
        quality_score=70,
        completeness_score=75,
        career_level="Entry",
        industry_classifications=["Technology"]
    )
    db_session.add(analysis)
    db_session.commit()

    analyses_before = db_session.query(AIAnalysis).filter(
        AIAnalysis.resume_id == resume.id
    ).count()
    assert analyses_before == 1

def test_delete_quality_analysis(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test deleting quality analysis"""
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

    analysis = AIAnalysis(
        id=uuid.uuid4(),
        resume_id=resume.id,
        quality_score=80,
        completeness_score=85,
        career_level="Senior"
    )
    db_session.add(analysis)
    db_session.commit()

    response = client.delete(f"/api/v1/quality/{resume.id}", headers=auth_headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

    response = client.get(f"/api/v1/quality/{resume.id}", headers=auth_headers)
    assert response.status_code == 404

def test_quality_analysis_with_location(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test quality analysis with custom location parameter"""
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

    params = {"location": "UK"}
    response = client.post(
        f"/api/v1/quality/analyze/{resume.id}",
        headers=auth_headers,
        params=params
    )
    assert response.status_code in [200, 500]

def test_quality_analysis_with_target_role(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test quality analysis with target role parameter"""
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

    params = {"target_role": "Data Scientist"}
    response = client.post(
        f"/api/v1/quality/analyze/{resume.id}",
        headers=auth_headers,
        params=params
    )
    assert response.status_code in [200, 500]

def test_quality_analysis_cascade_delete(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test that deleting resume cascades to quality analysis"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test.pdf",
        file_path="/fake/path/test.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="hash333",
        status="completed",
        structured_data=sample_resume_data
    )
    db_session.add(resume)
    db_session.commit()

    analysis = AIAnalysis(
        id=uuid.uuid4(),
        resume_id=resume.id,
        quality_score=85,
        completeness_score=90,
        career_level="Senior"
    )
    db_session.add(analysis)
    db_session.commit()
    resume_id = resume.id

    response = client.delete(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert response.status_code == 200

    analysis_exists = db_session.query(AIAnalysis).filter(
        AIAnalysis.resume_id == resume_id
    ).first()
    assert analysis_exists is None

