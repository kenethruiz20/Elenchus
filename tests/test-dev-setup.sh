#!/bin/bash

# Test Development Setup
# Validates that all development tools and configurations are properly set up

echo "🧪 Testing Development Setup"
echo "============================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -n "Testing $test_name... "
    
    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((TESTS_FAILED++))
    fi
}

# Prerequisites Tests
echo "🔍 Prerequisites:"
run_test "Node.js installation" "command -v node"
run_test "Python installation" "command -v python3"
run_test "Docker installation" "command -v docker"
run_test "Docker Compose" "command -v docker-compose"

echo ""

# Project Structure Tests
echo "📁 Project Structure:"
run_test "Frontend dependencies" "[ -d node_modules ]"
run_test "Backend virtual environment" "[ -d backend/venv ]"
run_test "Test scripts moved" "[ -d tests ] && [ -f tests/test-auth-flow.sh ]"
run_test "Development runners exist" "[ -f devrun.sh ] && [ -f devrun.js ]"

echo ""

# Configuration Tests  
echo "⚙️  Configuration Files:"
run_test "VS Code launch config" "[ -f .vscode/launch.json ]"
run_test "VS Code tasks config" "[ -f .vscode/tasks.json ]"
run_test "VS Code settings" "[ -f .vscode/settings.json ]"
run_test "Development documentation" "[ -f DEVELOPMENT.md ]"

echo ""

# Scripts Permissions
echo "🔧 Script Permissions:"
run_test "devrun.sh executable" "[ -x devrun.sh ]"
run_test "devrun.js executable" "[ -x devrun.js ]"
run_test "Test scripts executable" "[ -x tests/test-auth-flow.sh ]"

echo ""

# Backend Dependencies
echo "🐍 Backend Dependencies:"
if [ -d "backend/venv" ]; then
    run_test "FastAPI installed" "backend/venv/bin/python -c 'import fastapi'"
    run_test "Uvicorn installed" "backend/venv/bin/python -c 'import uvicorn'"
    run_test "Debugpy installed" "backend/venv/bin/python -c 'import debugpy'"
else
    echo -e "${YELLOW}⚠ Backend virtual environment not found - skipping dependency tests${NC}"
fi

echo ""

# Package.json Scripts
echo "📦 NPM Scripts:"
run_test "Package.json has dev script" "grep -q '\"dev\":' package.json"
run_test "Package.json has dev:full script" "grep -q '\"dev:full\":' package.json"
run_test "Package.json has test scripts" "grep -q '\"test\":' package.json"

echo ""

# Port Availability (optional check)
echo "🔌 Port Availability:"
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

run_test "Port 3000 available" "check_port 3000"
run_test "Port 8000 available" "check_port 8000"
run_test "Port 5678 available" "check_port 5678"

echo ""

# Summary
echo "📊 Test Results:"
echo "================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Development environment is ready.${NC}"
    echo -e "\n🚀 To start developing:"
    echo -e "   ./devrun.sh    (Shell version)"
    echo -e "   node devrun.js (Node.js version)"
    echo -e "   npm run dev:full (NPM script)"
    exit 0
else
    echo -e "\n${YELLOW}⚠ Some tests failed. Please check the setup instructions in DEVELOPMENT.md${NC}"
    exit 1
fi