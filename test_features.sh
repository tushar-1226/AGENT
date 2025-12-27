#!/bin/bash

# Test script for Project Management and Chat History features
# This script tests all backend endpoints to ensure they work properly

BASE_URL="http://localhost:8000"
USER_ID=1

echo "=========================================="
echo "Testing Friday Agent Features"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4

    echo -n "Testing: $name ... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        echo "  Response: $body"
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        FAILED=$((FAILED + 1))
        echo "  Error: $body"
    fi
    echo ""
}

# ===== PROJECT MANAGEMENT TESTS =====
echo "=========================================="
echo "1. PROJECT MANAGEMENT TESTS"
echo "=========================================="
echo ""

# Test 1: Create Project
test_endpoint \
    "Create Project" \
    "POST" \
    "/api/projects" \
    '{"name": "AI Assistant Project", "description": "Building an intelligent assistant", "user_id": 1, "metadata": {"priority": "high"}}'

# Test 2: Get All Projects
test_endpoint \
    "Get All Projects" \
    "GET" \
    "/api/projects?user_id=$USER_ID"

# Test 3: Create Another Project
test_endpoint \
    "Create Second Project" \
    "POST" \
    "/api/projects" \
    '{"name": "Code Generator", "description": "Automated code generation tool", "user_id": 1}'

# Test 4: Get Specific Project
test_endpoint \
    "Get Project by ID" \
    "GET" \
    "/api/projects/1"

# Test 5: Update Project
test_endpoint \
    "Update Project" \
    "PUT" \
    "/api/projects/1" \
    '{"name": "AI Assistant Project - Updated", "description": "Enhanced intelligent assistant with new features"}'

# Test 6: Get Updated Project
test_endpoint \
    "Get Updated Project" \
    "GET" \
    "/api/projects/1"

# ===== CHAT HISTORY TESTS =====
echo "=========================================="
echo "2. CHAT HISTORY TESTS"
echo "=========================================="
echo ""

# Test 7: Add Chat Message
test_endpoint \
    "Add Chat Message 1" \
    "POST" \
    "/api/chat/history" \
    '{"message": "How do I create a React component?", "response": "To create a React component, you can use either a function or a class. Here is an example of a functional component...", "project_id": 1, "user_id": 1}'

# Test 8: Add Another Chat Message
test_endpoint \
    "Add Chat Message 2" \
    "POST" \
    "/api/chat/history" \
    '{"message": "Explain Python decorators", "response": "Python decorators are a powerful feature that allows you to modify the behavior of functions or classes...", "user_id": 1}'

# Test 9: Add Third Chat Message
test_endpoint \
    "Add Chat Message 3" \
    "POST" \
    "/api/chat/history" \
    '{"message": "What is async/await in JavaScript?", "response": "Async/await is syntactic sugar built on top of promises, making asynchronous code look and behave more like synchronous code...", "project_id": 2, "user_id": 1}'

# Test 10: Get All Chat History
test_endpoint \
    "Get All Chat History" \
    "GET" \
    "/api/chat/history?user_id=$USER_ID&limit=100"

# Test 11: Get Chat History for Specific Project
test_endpoint \
    "Get Chat History for Project 1" \
    "GET" \
    "/api/chat/history?project_id=1&user_id=$USER_ID"

# Test 12: Search Chat History - "React"
test_endpoint \
    "Search Chat History (React)" \
    "GET" \
    "/api/chat/search?q=React&user_id=$USER_ID&limit=50"

# Test 13: Search Chat History - "Python"
test_endpoint \
    "Search Chat History (Python)" \
    "GET" \
    "/api/chat/search?q=Python&user_id=$USER_ID&limit=50"

# Test 14: Search Chat History - "async"
test_endpoint \
    "Search Chat History (async)" \
    "GET" \
    "/api/chat/search?q=async&user_id=$USER_ID&limit=50"

# ===== EDGE CASES =====
echo "=========================================="
echo "3. EDGE CASE TESTS"
echo "=========================================="
echo ""

# Test 15: Create Project without name (should fail)
echo -n "Testing: Create Project without name ... "
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/projects" \
    -H "Content-Type: application/json" \
    -d '{"description": "No name project", "user_id": 1}')
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "400" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Expected 400 error)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC} (Expected 400, got $http_code)"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 16: Get non-existent project (should return 404)
echo -n "Testing: Get Non-existent Project ... "
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/projects/9999")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "404" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Expected 404 error)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC} (Expected 404, got $http_code)"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 17: Search with empty query (should fail)
echo -n "Testing: Search with Empty Query ... "
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/chat/search?q=&user_id=$USER_ID")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "400" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Expected 400 error)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC} (Expected 400, got $http_code)"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 18: Delete Project
test_endpoint \
    "Delete Project" \
    "DELETE" \
    "/api/projects/2"

# Test 19: Verify Deleted Project
echo -n "Testing: Verify Project Deleted ... "
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/projects/2")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "404" ]; then
    echo -e "${GREEN}✓ PASSED${NC} (Project successfully deleted)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC} (Project still exists)"
    FAILED=$((FAILED + 1))
fi
echo ""

# ===== SUMMARY =====
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
TOTAL=$((PASSED + FAILED))
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed!${NC}"
    exit 1
fi
