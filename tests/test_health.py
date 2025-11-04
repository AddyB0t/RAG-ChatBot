"""
Test health and basic endpoints
"""
import pytest
from fastapi.testclient import TestClient

def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["version"] == "2.1.0"

def test_health_endpoint(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert data["database"] == "connected"

def test_health_endpoint_no_auth_required(client: TestClient):
    """Verify health endpoint doesn't require authentication"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

def test_api_documentation_available(client: TestClient):
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200

def test_openapi_schema(client: TestClient):
    """Test OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["version"] == "2.1.0"

