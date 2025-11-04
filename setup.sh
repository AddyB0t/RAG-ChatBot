#!/bin/bash

# AI-Powered Resume Parser - Setup Script
# Version: 2.1.0
# Description: Automated setup script for local development environment

set -e  # Exit on error

echo "=================================="
echo "AI Resume Parser Setup Script"
echo "Version: 2.1.0"
echo "=================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_warning "This script is optimized for Linux. You may need to adjust for your OS."
fi

# Step 1: Check Python installation
echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

# Step 2: Check PostgreSQL installation
echo ""
echo "Step 2: Checking PostgreSQL installation..."
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version | cut -d' ' -f3)
    print_success "PostgreSQL found: $PG_VERSION"
else
    print_warning "PostgreSQL not found. Installing PostgreSQL..."
    sudo apt-get update
    sudo apt-get install -y postgresql postgresql-contrib
    print_success "PostgreSQL installed"
fi

# Step 3: Check if PostgreSQL service is running
echo ""
echo "Step 3: Starting PostgreSQL service..."
if sudo systemctl is-active --quiet postgresql; then
    print_success "PostgreSQL service is already running"
else
    sudo systemctl start postgresql
    print_success "PostgreSQL service started"
fi

# Step 4: Create database and user
echo ""
echo "Step 4: Setting up database..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'hackathon'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE DATABASE hackathon;"
print_success "Database 'hackathon' ready"

# Set password for postgres user (for local development)
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
print_success "Database user configured"

# Step 5: Check for conda/miniconda
echo ""
echo "Step 5: Setting up Python environment..."
if [ -d "/mnt/data/miniconda3" ]; then
    print_success "Miniconda found at /mnt/data/miniconda3"
    source /mnt/data/miniconda3/bin/activate

    # Check if Hackathon environment exists
    if conda env list | grep -q "Hackathon"; then
        print_success "Conda environment 'Hackathon' already exists"
        conda activate Hackathon
    else
        print_info "Creating conda environment 'Hackathon'..."
        conda create -n Hackathon python=3.11 -y
        conda activate Hackathon
        print_success "Conda environment 'Hackathon' created"
    fi
else
    print_warning "Miniconda not found. Using system Python and venv..."

    # Install venv if not present
    sudo apt-get install -y python3-venv

    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi

    source venv/bin/activate
    print_success "Virtual environment activated"
fi

# Step 6: Install Python dependencies
echo ""
echo "Step 6: Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Step 7: Create .env file if not exists
echo ""
echo "Step 7: Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Created .env from .env.example"
        print_warning "IMPORTANT: Edit .env and add your OPENAI_API_KEY!"
    else
        print_warning "Creating default .env file..."
        cat > .env << EOF
# OpenRouter AI Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=openai/gpt-4o

# Database Configuration
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hackathon

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True
AUTH_PASSWORD=QWERTY

# File Upload Configuration
MAX_FILE_SIZE_MB=5
ALLOWED_EXTENSIONS=pdf,docx,doc,txt
UPLOAD_DIR=uploads

# Logging
LOG_LEVEL=INFO
EOF
        print_warning "Created default .env file"
        print_warning "IMPORTANT: Edit .env and add your OPENAI_API_KEY!"
    fi
else
    print_success ".env file already exists"
fi

# Step 8: Create necessary directories
echo ""
echo "Step 8: Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
print_success "Directories created"

# Step 9: Initialize database tables
echo ""
echo "Step 9: Initializing database tables..."
python3 << EOF
import sys
sys.path.insert(0, '.')
try:
    from app.core.database import engine, Base
    from app.models.database import Resume, ResumeJobMatch, AIAnalysis, ResumeParserErrorLog
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating database tables: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Database tables initialized"
else
    print_error "Failed to initialize database tables"
    exit 1
fi

# Step 10: Verify installation
echo ""
echo "Step 10: Verifying installation..."

# Check if all required packages are installed
python3 << EOF
try:
    import fastapi
    import sqlalchemy
    import uvicorn
    import PyPDF2
    import docx
    import requests
    print("All required packages are installed")
except ImportError as e:
    print(f"Missing package: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "All dependencies verified"
else
    print_error "Some dependencies are missing"
    exit 1
fi

# Step 11: Test database connection
echo ""
echo "Step 11: Testing database connection..."
python3 << EOF
import sys
sys.path.insert(0, '.')
try:
    from app.core.database import SessionLocal
    db = SessionLocal()
    db.execute("SELECT 1")
    db.close()
    print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Database connection successful"
else
    print_error "Database connection failed"
    exit 1
fi

# Final summary
echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
print_success "Project setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENAI_API_KEY"
echo "2. Start the server with one of these commands:"
echo ""
if [ -d "/mnt/data/miniconda3" ]; then
    echo "   source /mnt/data/miniconda3/bin/activate Hackathon"
else
    echo "   source venv/bin/activate"
fi
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Access the API documentation at:"
echo "   http://localhost:8000/docs"
echo ""
echo "4. Test the API with:"
echo "   curl http://localhost:8000/api/v1/health"
echo ""
print_info "Default API password is: QWERTY (change in .env)"
echo ""
print_warning "Remember to never commit your .env file to version control!"
echo ""
echo "For more information, see:"
echo "  - README.md - General documentation"
echo "  - PROJECT_SUMMARY.md - Complete feature overview"
echo "  - REQUIREMENTS_CHECKLIST.md - Hackathon compliance"
echo ""
print_success "Happy coding! 🚀"
