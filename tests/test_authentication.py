"""
Test authentication and security
"""
import pytest
from fastapi.testclient import TestClient

def test_missing_auth_token(client: TestClient):
    """Test that endpoints reject requests without authentication"""
    response = client.get("/api/v1/resumes/")
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert "Authorization header" in data["detail"]

def test_invalid_auth_token(client: TestClient):
    """Test that endpoints reject invalid tokens"""
    headers = {"Authorization": "Bearer INVALID_TOKEN"}
    response = client.get("/api/v1/resumes/", headers=headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert "Invalid credentials" in data["detail"]

def test_valid_auth_token(client: TestClient, auth_headers: dict):
    """Test that valid token grants access"""
    response = client.get("/api/v1/resumes/", headers=auth_headers)
    assert response.status_code != 403

def test_auth_token_case_sensitive(client: TestClient):
    """Test that auth is case-sensitive"""
    headers = {"authorization": "Bearer QWERTY"}
    response = client.get("/api/v1/resumes/", headers=headers)
    assert response.status_code != 403

def test_missing_bearer_prefix(client: TestClient):
    """Test that token without 'Bearer' prefix is rejected"""
    headers = {"Authorization": "QWERTY"}
    response = client.get("/api/v1/resumes/", headers=headers)
    assert response.status_code == 403

def test_protected_endpoints_require_auth(client: TestClient, auth_headers: dict):
    """Test that all protected endpoints require authentication"""
    protected_endpoints = [
        ("/api/v1/resumes/", "GET"),
        ("/api/v1/resumes/upload", "POST"),
    ]

    for endpoint, method in protected_endpoints:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint)

        assert response.status_code == 403, f"{method} {endpoint} should require auth"

        if method == "GET":
            response = client.get(endpoint, headers=auth_headers)
        else:
            response = client.post(endpoint, headers=auth_headers)

        assert response.status_code != 403, f"{method} {endpoint} should accept valid auth"

