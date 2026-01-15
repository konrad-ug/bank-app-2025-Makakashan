#!/bin/bash
# Test Summary Script - Runs all test suites and displays results

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║           Bank Application - Test Suite Summary           ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Activate virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate 2>/dev/null || source venv/bin/activate 2>/dev/null || {
        echo "Error: Could not activate virtual environment"
        exit 1
    }
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}1. Unit Tests${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -m pytest tests/unit/ -v --tb=line
UNIT_RESULT=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}2. API Tests${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python -m pytest tests/api/ -v --tb=line
API_RESULT=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}3. Coverage Report${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
coverage run -m pytest tests/unit/ tests/api/ -q
coverage report

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}4. Performance Tests (requires Flask)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Starting Flask server...${NC}"

export FLASK_APP=app/api.py
export FLASK_ENV=development
export PYTHONPATH=$PWD

flask run > /dev/null 2>&1 &
FLASK_PID=$!
sleep 5

if curl -s http://localhost:5000/ > /dev/null 2>&1; then
    echo -e "${GREEN}Flask running (PID: $FLASK_PID)${NC}"
    python -m pytest tests/perf/ -v --tb=line
    PERF_RESULT=$?
    kill $FLASK_PID 2>/dev/null || true
    echo -e "${GREEN}Flask stopped${NC}"
else
    echo "Error: Flask failed to start"
    kill $FLASK_PID 2>/dev/null || true
    PERF_RESULT=1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                      Test Summary                          ║"
echo "╠════════════════════════════════════════════════════════════╣"

if [ $UNIT_RESULT -eq 0 ]; then
    echo -e "║  Unit Tests:        ${GREEN}✓ PASSED${NC}                              ║"
else
    echo -e "║  Unit Tests:        ${RED}✗ FAILED${NC}                              ║"
fi

if [ $API_RESULT -eq 0 ]; then
    echo -e "║  API Tests:         ${GREEN}✓ PASSED${NC}                              ║"
else
    echo -e "║  API Tests:         ${RED}✗ FAILED${NC}                              ║"
fi

if [ $PERF_RESULT -eq 0 ]; then
    echo -e "║  Performance Tests: ${GREEN}✓ PASSED${NC}                              ║"
else
    echo -e "║  Performance Tests: ${RED}✗ FAILED${NC}                              ║"
fi

echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Exit with error if any test failed
if [ $UNIT_RESULT -ne 0 ] || [ $API_RESULT -ne 0 ] || [ $PERF_RESULT -ne 0 ]; then
    exit 1
fi

exit 0
