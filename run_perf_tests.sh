#!/bin/bash
# Script to run performance tests with Flask server

set -e

echo "=================================="
echo "Performance Tests Runner"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate || source venv/bin/activate || {
        echo -e "${RED}Error: Could not activate virtual environment${NC}"
        exit 1
    }
fi

# Set Flask environment variables
export FLASK_APP=app/api.py
export FLASK_ENV=development
export PYTHONPATH=$PWD

# Start Flask server
echo -e "${YELLOW}Starting Flask server...${NC}"
flask run > flask.log 2>&1 &
FLASK_PID=$!
echo $FLASK_PID > flask.pid

# Wait for Flask to start
echo "Waiting for Flask to start..."
sleep 5

# Check if Flask is running
if curl -s http://localhost:5000/ > /dev/null; then
    echo -e "${GREEN}Flask server is running (PID: $FLASK_PID)${NC}"
else
    echo -e "${RED}Error: Flask server failed to start${NC}"
    kill $FLASK_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "=================================="
echo "Running Performance Tests"
echo "=================================="
echo ""

# Run performance tests
if python -m pytest tests/perf/ -v; then
    echo ""
    echo -e "${GREEN}All performance tests passed!${NC}"
    TEST_RESULT=0
else
    echo ""
    echo -e "${RED}Some performance tests failed!${NC}"
    TEST_RESULT=1
fi

# Stop Flask server
echo ""
echo -e "${YELLOW}Stopping Flask server...${NC}"
kill $FLASK_PID 2>/dev/null || true
rm -f flask.pid
sleep 1

echo -e "${GREEN}Flask server stopped${NC}"
echo ""
echo "=================================="
echo "Performance Tests Complete"
echo "=================================="

exit $TEST_RESULT
