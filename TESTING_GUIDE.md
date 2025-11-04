# Testing Guide
## AI-Powered Resume Parser & Job Matcher

This document provides comprehensive testing instructions for the application.

---

## Quick Start

### Run All Tests
```bash
# Option 1: Using test runner script
./run_tests.sh

# Option 2: Direct pytest command
pytest tests/ -v

# Option 3: With coverage report
pytest tests/ -v --cov=app --cov-report=html
```

### Run Specific Test Files
```bash
# Test authentication only
pytest tests/test_authentication.py -v

# Test health endpoints
pytest tests/test_health.py -v

# Test resume management
pytest tests/test_resumes.py -v

# Test job matching
pytest tests/test_job_matching.py -v

# Test quality analysis
pytest tests/test_quality_analysis.py -v
```

---

## Test Suite Overview

### Test Files (5 files, 40+ tests)

1. **test_health.py** - Health check and basic endpoints
   - Root endpoint information
   - Health check with database
   - API documentation accessibility
   - OpenAPI schema validation

2. **test_authentication.py** - Security and authentication
   - Missing auth token rejection
   - Invalid token rejection
   - Valid token acceptance
   - Bearer prefix requirement
   - Protected endpoint verification

3. **test_resumes.py** - Resume management endpoints
   - List resumes (empty and populated)
   - Upload resume validation
   - Get resume by ID
   - Resume not found handling
   - Status checking
   - Delete resume
   - Update resume
   - Duplicate detection

4. **test_job_matching.py** - Job matching functionality
   - Match with non-existent resume
   - Match with incomplete resume
   - Required field validation
   - Get match details
   - List resume matches
   - Delete match
   - Create and retrieve matches

5. **test_quality_analysis.py** - Quality analysis endpoints
   - Analyze non-existent resume
   - Analyze incomplete resume
   - Get analysis not found
   - Create and retrieve analysis
   - Update existing analysis
   - Delete analysis
   - Location and target role parameters
   - Cascade delete verification

---

## Test Coverage

### What's Tested
✅ All API endpoints (16 endpoints)
✅ Authentication and security
✅ Database operations (CRUD)
✅ Error handling (404, 400, 422, 403)
✅ Data validation
✅ Cascade deletes
✅ Parameter handling

### What's NOT Tested (Requires AI/External Services)
⚠️ Actual file upload processing (mocked)
⚠️ AI extraction quality (requires OpenAI API)
⚠️ Job matching algorithm accuracy (requires AI)
⚠️ Quality analysis scoring (requires AI)

---

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio httpx

# Or from requirements.txt
pip install -r requirements.txt
```

### Test Modes

#### 1. Quick Test (No Coverage)
```bash
pytest tests/ -v
```

#### 2. With Coverage Report
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

#### 3. Generate HTML Coverage Report
```bash
pytest tests/ -v --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

#### 4. Run Specific Test
```bash
# Run single test function
pytest tests/test_health.py::test_root_endpoint -v

# Run test class
pytest tests/test_authentication.py::TestAuthentication -v
```

#### 5. Run Tests by Marker
```bash
# Run only auth tests (if markers are added)
pytest -m auth -v

# Run only API tests
pytest -m api -v
```

---

## Test Database

Tests use an **in-memory SQLite database** that is:
- Created fresh for each test function
- Automatically cleaned up after each test
- Isolated from production database
- Fast and doesn't require PostgreSQL

This is configured in `tests/conftest.py`:
```python
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
```

---

## Test Fixtures

Available fixtures in `conftest.py`:

### `client`
FastAPI test client with database override
```python
def test_example(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
```

### `auth_headers`
Authentication headers for protected endpoints
```python
def test_example(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/resumes/", headers=auth_headers)
```

### `db_session`
Database session for direct database manipulation
```python
def test_example(db_session: Session):
    resume = Resume(...)
    db_session.add(resume)
    db_session.commit()
```

### `sample_resume_data`
Pre-configured resume data for testing
```python
def test_example(sample_resume_data: dict):
    assert sample_resume_data["name"]["full_name"] == "John Doe"
```

### `sample_job_description`
Pre-configured job description for testing
```python
def test_example(sample_job_description: dict):
    assert sample_job_description["job_title"] == "Senior Software Engineer"
```

---

## Writing New Tests

### Test Template
```python
def test_your_feature(client: TestClient, auth_headers: dict):
    """Test description"""
    # Arrange
    data = {"key": "value"}

    # Act
    response = client.post("/api/v1/endpoint", headers=auth_headers, json=data)

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert result["key"] == "expected_value"
```

### Best Practices
1. **Use descriptive test names**: `test_upload_resume_invalid_format`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test one thing per test**: Keep tests focused
4. **Use fixtures**: Avoid repetitive setup code
5. **Test edge cases**: Empty data, invalid IDs, missing fields
6. **Mock external services**: Don't depend on AI/network calls

---

## Continuous Integration

### GitHub Actions (Example)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v --cov=app
```

---

## Troubleshooting

### Import Errors
```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use pytest's default discovery
pytest
```

### Database Errors
```bash
# Tests use SQLite, not PostgreSQL
# If you see PostgreSQL errors, check conftest.py
```

### Fixture Not Found
```bash
# Ensure conftest.py is in tests/ directory
ls tests/conftest.py

# Ensure __init__.py exists
ls tests/__init__.py
```

### Test Hangs
```bash
# Some tests may timeout waiting for AI
# These are expected and can be skipped
pytest -k "not slow" -v
```

---

## Test Metrics

### Current Coverage
- **Total Tests**: 40+
- **Test Files**: 5
- **Lines of Test Code**: 1,000+
- **Estimated Coverage**: 70-80% (excluding AI processing)

### Test Execution Time
- **All tests**: ~5-10 seconds
- **Individual file**: ~1-2 seconds
- **Single test**: < 1 second

---

## Manual Testing

### Using Swagger UI
1. Start server: `uvicorn app.main:app --reload`
2. Open browser: http://localhost:8000/docs
3. Click "Authorize" and enter: `QWERTY`
4. Test endpoints interactively

### Using cURL
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload resume
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -H "Authorization: Bearer QWERTY" \
  -F "file=@sample_resume.pdf"

# List resumes
curl http://localhost:8000/api/v1/resumes/ \
  -H "Authorization: Bearer QWERTY"
```

### Using Postman
Import the OpenAPI spec from: http://localhost:8000/openapi.json

---

## Performance Testing

### Load Testing (Optional)
```bash
# Install locust
pip install locust

# Create locustfile.py
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

---

## Next Steps

1. ✅ Run test suite: `./run_tests.sh`
2. ✅ Check coverage: Open `htmlcov/index.html`
3. ✅ Fix any failing tests
4. ✅ Add tests for new features
5. ✅ Integrate with CI/CD

---

**For more information**:
- Main README: [README.md](README.md)
- Project Summary: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- Requirements Checklist: [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md)
