# AI-Powered Resume Parser & Job Matcher

**Version**: 2.2.0
**Status**: Production Ready

---

## Overview

A comprehensive AI-powered system for parsing resumes, extracting structured information, and matching candidates to job requirements. Features advanced capabilities including bias detection, resume anonymization, competitive analysis, and intelligent candidate ranking.

## Key Features

### Core Functionality

- **Resume Parsing**: Extract structured data from PDF, DOCX, DOC, TXT formats
- **OCR Support**: Process scanned documents using Tesseract OCR
- **Named Entity Recognition**: Extract entities using Flair NER models
- **Job Matching**: Intelligent matching algorithm with multi-criteria scoring

### Advanced Features

- **Bias Detection**: Identify and flag potential biases across 7 categories
- **Resume Anonymization**: Remove PII with 10 customizable options
- **Competitive Analysis**: Benchmark candidates against industry standards
- **Candidate Ranking**: Multi-criteria ranking with S/A/B/C/D tiers
- **Quality Analysis**: Comprehensive resume quality assessment

### API Features

- RESTful API with FastAPI
- Interactive documentation (Swagger/ReDoc)
- Rate limiting and authentication
- Error tracking and logging
- Health monitoring

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Tesseract OCR
- 4GB+ RAM
- 10GB+ disk space

### Installation

#### 1. Clone Repository

```bash
git clone <repository-url>
cd RAG-ChatBot
```

#### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Install System Dependencies

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
```

**macOS:**

```bash
brew install tesseract poppler
```

**Windows:**

- Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH

#### 4. Set Up PostgreSQL

```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE resume_db;"

# Create user (optional)
sudo -u postgres psql -c "CREATE USER resume_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE resume_db TO resume_user;"
```

#### 5. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required variables:

```env
OPENROUTER_API_KEY=your_api_key_here
DB_NAME=resume_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

#### 6. Start Application

```bash
# Using the startup script
./start_server.sh

# Or manually
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the application:

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

---

## Docker Deployment

### Quick Start with Docker

**Step 1: Configure API Key**

Before running Docker, you need to set up your OpenAI API key:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

Update this line in `.env`:
```
OPENROUTER_API_KEY=your-actual-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

**Step 2: Run the Application**

Two simple commands to run the entire application:

```bash
# Build the application
docker-compose build app

# Start all services (database + application)
docker-compose up --build
```

That's it! The application will be available at http://localhost:8000

### Alternative: Run in Background

```bash
# Build the application
docker-compose build app

# Start in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Check status
docker-compose ps

# Stop services
docker-compose down
```

### Docker Commands Reference

```bash
# Build only the app service
docker-compose build app

# Start services (rebuild if needed)
docker-compose up --build

# Start in background
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Restart services
docker-compose restart app

# Access container shell
docker-compose exec app bash

**Access Points:**

- API: http://localhost:8000
- Database: localhost:5433

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed documentation.

---

## API Documentation

### Authentication

All endpoints require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_PASSWORD" \
  http://localhost:8000/api/v1/endpoint
```

### Core Endpoints

#### Upload Resume

```bash
POST /api/v1/resumes/upload
Content-Type: multipart/form-data

# Example
curl -X POST \
  -H "Authorization: Bearer QWERTY" \
  -F "file=@resume.pdf" \
  http://localhost:8000/api/v1/resumes/upload
```

#### Match Resume to Job

```bash
POST /api/v1/job-matching/match/{resume_id}
Content-Type: application/json

{
  "job_title": "Software Engineer",
  "job_description": "Looking for a Python developer...",
  "required_skills": ["Python", "FastAPI", "PostgreSQL"]
}
```

#### Quality Analysis

```bash
POST /api/v1/quality/analyze/{resume_id}?target_role=Software%20Engineer
```

### Advanced Endpoints

#### Bias Detection

```bash
POST /api/v1/advanced/bias-detection/{resume_id}
```

#### Resume Anonymization

```bash
POST /api/v1/advanced/anonymize
{
  "resume_data": {...},
  "options": {
    "remove_name": true,
    "remove_contact": true,
    "remove_address": true
  }
}
```

#### Candidate Ranking

```bash
POST /api/v1/advanced/rank-candidates
{
  "candidates": [...],
  "job_requirements": {...}
}
```

#### Candidate Comparison

```bash
POST /api/v1/advanced/candidate-comparison?candidate1_id=xxx&candidate2_id=yyy
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           FastAPI Application               │
├─────────────────────────────────────────────┤
│  API Routes  │  Services   │  ML Models     │
│  - Resumes   │  - Parser   │  - Flair NER   │
│  - Matching  │  - Matcher  │  - OpenAI  │
│  - Quality   │  - Quality  │                │
│  - Advanced  │  - Bias     │                │
│              │  - Ranker   │                │
├─────────────────────────────────────────────┤
│         PostgreSQL Database                 │
│  - Resumes   - Job Matches   - Error Logs  │
└─────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**

- FastAPI 0.104.1
- Python 3.11
- Pydantic 2.12.1
- Uvicorn

**Database:**

- PostgreSQL 14+
- SQLAlchemy 2.0.23
- Psycopg2 2.9.9

**ML/AI:**

- Flair 0.13.1 (NER)
- OpenAI API (LLM)
- Torch 2.1.1

**Document Processing:**

- PyPDF2 3.0.1
- python-docx 1.1.0
- Tesseract OCR
- Poppler

---

## Project Structure

```
RAG-ChatBot/
├── app/
│   ├── api/routes/            # API endpoints
│   ├── core/                  # Core configuration
│   ├── models/                # Database models
│   ├── services/              # Business logic
│   └── main.py                # Application entry
├── tests/                     # Test suite
├── uploads/                   # Resume storage
├── logs/                      # Application logs
├── models/                    # ML model cache
├── docker-compose.yml         # Docker setup
├── Dockerfile                 # Docker image
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

---

## Configuration

### Environment Variables

**Required:**

- `OPENROUTER_API_KEY` - OpenAI API key for LLM access

**Database:**

- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5432)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

**API:**

- `API_HOST` - API bind host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `API_WORKERS` - Number of workers (default: 4)
- `AUTH_PASSWORD` - Bearer token password

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## Performance

### Benchmarks

- Resume parsing: ~2-5 seconds per document
- Job matching: ~1-3 seconds per match
- Bias detection: ~0.5-1 second per resume
- Candidate ranking: ~0.1 seconds per candidate

---

## Security

### Best Practices

1. **Protect API Keys**:
   - Never commit `.env` files to version control
   - Never hardcode API keys in `docker-compose.yml` or source code
   - Use environment variables for all sensitive credentials
   - Regenerate API keys immediately if accidentally exposed

2. **Change Default Password**: Update `AUTH_PASSWORD` in production

3. **Secure Database**: Use strong passwords and limit access

4. **HTTPS**: Use reverse proxy (nginx) with SSL/TLS

5. **Rate Limiting**: Configure appropriate limits

---

## Support

For issues or questions:

- Open an issue on GitHub
- Check documentation files
- Review test cases for usage examples

---

## Changelog

### Version 2.2.0 (2025-11-04)

- Added bias detection system
- Implemented resume anonymization
- Added competitive analysis
- Implemented candidate ranking system
- Enhanced candidate comparison
- Docker deployment support
- Comprehensive test suite

---

**Built with FastAPI, PostgreSQL, and AI**
