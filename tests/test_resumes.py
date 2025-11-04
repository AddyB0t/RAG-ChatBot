"""
Test resume management endpoints
"""
import pytest
import uuid
import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.database import Resume

def test_list_resumes_empty(client: TestClient, auth_headers: dict):
    """Test listing resumes when database is empty"""
    response = client.get("/api/v1/resumes/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_upload_resume_missing_file(client: TestClient, auth_headers: dict):
    """Test upload without file returns error"""
    response = client.post("/api/v1/resumes/upload", headers=auth_headers)
    assert response.status_code == 422

def test_upload_resume_invalid_format(client: TestClient, auth_headers: dict):
    """Test upload with invalid file format"""
    files = {"file": ("test.exe", io.BytesIO(b"fake executable"), "application/x-msdownload")}
    response = client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert response.status_code in [400, 422]

def test_upload_resume_success_mock(client: TestClient, auth_headers: dict, db_session: Session):
    """Test successful resume upload (mocked - no actual file processing)"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test_resume.pdf",
        file_path="/fake/path/test_resume.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="fakehash123",
        status="completed",
        structured_data={"name": {"full_name": "Test User"}}
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)

    response = client.get("/api/v1/resumes/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["file_name"] == "test_resume.pdf"

def test_get_resume_by_id(client: TestClient, auth_headers: dict, db_session: Session):
    """Test retrieving a resume by ID"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test_resume.pdf",
        file_path="/fake/path/test_resume.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="fakehash456",
        status="completed",
        structured_data={"name": {"full_name": "Jane Doe"}}
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)

    response = client.get(f"/api/v1/resumes/{resume.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test_resume.pdf"
    assert data["structured_data"]["name"]["full_name"] == "Jane Doe"

def test_get_resume_not_found(client: TestClient, auth_headers: dict):
    """Test retrieving non-existent resume returns 404"""
    fake_id = uuid.uuid4()
    response = client.get(f"/api/v1/resumes/{fake_id}", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_get_resume_status(client: TestClient, auth_headers: dict, db_session: Session):
    """Test getting resume processing status"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test_resume.pdf",
        file_path="/fake/path/test_resume.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="fakehash789",
        status="processing"
    )
    db_session.add(resume)
    db_session.commit()
    db_session.refresh(resume)

    response = client.get(f"/api/v1/resumes/{resume.id}/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"

def test_delete_resume(client: TestClient, auth_headers: dict, db_session: Session):
    """Test deleting a resume"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test_resume.pdf",
        file_path="/fake/path/test_resume.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="fakehash999",
        status="completed"
    )
    db_session.add(resume)
    db_session.commit()
    resume_id = resume.id

    response = client.delete(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert response.status_code == 200

    response = client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert response.status_code == 404

def test_update_resume(client: TestClient, auth_headers: dict, db_session: Session, sample_resume_data: dict):
    """Test updating resume data"""
    resume = Resume(
        id=uuid.uuid4(),
        file_name="test_resume.pdf",
        file_path="/fake/path/test_resume.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="fakehash111",
        status="completed",
        structured_data={"name": {"full_name": "Old Name"}}
    )
    db_session.add(resume)
    db_session.commit()
    resume_id = resume.id

    update_data = {"structured_data": sample_resume_data}
    response = client.put(
        f"/api/v1/resumes/{resume_id}",
        headers=auth_headers,
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["structured_data"]["name"]["full_name"] == "John Doe"

def test_duplicate_resume_detection(client: TestClient, auth_headers: dict, db_session: Session):
    """Test that duplicate resumes are detected by file hash"""
    resume1 = Resume(
        id=uuid.uuid4(),
        file_name="resume1.pdf",
        file_path="/fake/path/resume1.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="duplicate_hash",
        status="completed"
    )
    db_session.add(resume1)
    db_session.commit()

    resume2 = Resume(
        id=uuid.uuid4(),
        file_name="resume2.pdf",
        file_path="/fake/path/resume2.pdf",
        file_size=1024,
        file_type="application/pdf",
        file_hash="duplicate_hash",
        status="completed"
    )

    with pytest.raises(Exception):
        db_session.add(resume2)
        db_session.commit()

