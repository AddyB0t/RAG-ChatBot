#!/bin/bash

# AI-Powered Resume Parser - Test Runner
# Runs the complete test suite with coverage reporting

echo "=================================="
echo "Running Test Suite"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! python3 -c "import pytest" &> /dev/null; then
    echo -e "${RED}Error: pytest not installed${NC}"
    echo "Install with: pip install pytest pytest-cov pytest-asyncio"
    exit 1
fi

# Run tests with coverage
echo -e "${YELLOW}Running tests with coverage...${NC}"
echo ""

pytest tests/ \
    -v \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --tb=short

TEST_EXIT_CODE=$?

echo ""
echo "=================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

echo "=================================="
echo ""

# Show coverage report location
if [ -d "htmlcov" ]; then
    echo -e "${YELLOW}Coverage report generated:${NC}"
    echo "  Open: htmlcov/index.html"
    echo ""
fi

# Test summary
echo "Test summary:"
echo "  - Unit tests: tests/test_*.py"
echo "  - Coverage report: htmlcov/index.html"
echo ""

exit $TEST_EXIT_CODE
