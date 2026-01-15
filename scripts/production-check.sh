#!/bin/bash

# Production Readiness Check Script
# Validates your deployment configuration before going live

set -e

echo "=================================="
echo "  Production Readiness Check"
echo "=================================="
echo ""

ERRORS=0
WARNINGS=0

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Helper functions
error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
    ((ERRORS++))
}

warn() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}"
    ((WARNINGS++))
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 1. Check Docker installation
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    success "Docker installed: $DOCKER_VERSION"
else
    error "Docker is not installed. Install from https://docs.docker.com/get-docker/"
fi

if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    success "Docker Compose is available"
else
    error "Docker Compose is not installed"
fi
echo ""

# 2. Check environment files
echo "2. Checking environment configuration..."

if [ -f "backend/.env" ]; then
    success "backend/.env exists"
    
    # Check for required variables
    if grep -q "^GEMINI_API_KEY=AIza" backend/.env; then
        success "GEMINI_API_KEY is set"
    elif grep -q "^GEMINI_API_KEY=your" backend/.env; then
        error "GEMINI_API_KEY is not configured (still has placeholder value)"
    else
        warn "GEMINI_API_KEY may not be properly configured"
    fi
    
    if grep -q "^FRONTEND_URL=http://localhost:3000" backend/.env; then
        warn "FRONTEND_URL is set to localhost (update for production)"
    fi
else
    error "backend/.env not found. Copy from backend/.env.example"
fi

if [ -f "frontend/.env.local" ]; then
    success "frontend/.env.local exists"
else
    warn "frontend/.env.local not found (will use default API URL)"
fi
echo ""

# 3. Check .gitignore
echo "3. Checking .gitignore configuration..."
if [ -f ".gitignore" ]; then
    if grep -q ".env" .gitignore; then
        success ".env files are ignored by Git"
    else
        error ".env files are NOT ignored - SECURITY RISK!"
    fi
    
    if grep -q "\.next/" .gitignore; then
        success ".next build directory is ignored"
    else
        warn ".next directory should be in .gitignore"
    fi
else
    error ".gitignore not found"
fi
echo ""

# 4. Check for secrets in Git
echo "4. Checking for exposed secrets..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git ls-files | grep -q "\.env$"; then
        error ".env files are tracked by Git - SECURITY RISK!"
        echo "  Run: git rm --cached backend/.env frontend/.env.local"
    else
        success "No .env files tracked by Git"
    fi
    
    # Check for API keys in committed files
    if git grep -q "AIza[0-9A-Za-z_-]\{35\}" 2>/dev/null; then
        error "Potential API keys found in Git history - SECURITY RISK!"
    else
        success "No obvious API keys in Git"
    fi
else
    warn "Not a Git repository"
fi
echo ""

# 5. Check Docker files
echo "5. Checking Docker configuration..."
for file in Dockerfile.backend Dockerfile.frontend docker-compose.yml .dockerignore; do
    if [ -f "$file" ]; then
        success "$file exists"
    else
        error "$file not found"
    fi
done
echo ""

# 6. Check file permissions
echo "6. Checking file permissions..."
if [ -x "deploy.sh" ]; then
    success "deploy.sh is executable"
else
    warn "deploy.sh is not executable (run: chmod +x deploy.sh)"
fi

if [ -f "backend/users.db" ]; then
    if [ -w "backend/users.db" ]; then
        success "Database files are writable"
    else
        error "Database files are not writable"
    fi
fi
echo ""

# 7. Check Node.js dependencies (if needed)
echo "7. Checking dependencies..."
if [ -d "frontend/node_modules" ]; then
    success "Frontend dependencies installed"
else
    warn "Frontend dependencies not installed (run: cd frontend && npm install)"
fi

if [ -d "backend/venv" ]; then
    success "Backend virtual environment exists"
else
    warn "Backend virtual environment not found (run: cd backend && python -m venv venv)"
fi
echo ""

# 8. Security audit
echo "8. Security audit..."
if [ -f "backend/.env" ]; then
    # Check if using default/example API keys
    if grep -q "your_.*_key_here" backend/.env; then
        warn "Some API keys still have placeholder values"
    fi
    
    # Check CORS configuration
    if grep -q "allow_origins=\[\"*\"\]" backend/app/main.py; then
        warn "CORS allows all origins (*) - should restrict to your domain in production"
    fi
fi
echo ""

# Summary
echo "=================================="
echo "  Summary"
echo "=================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready for deployment.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found. Review before deploying.${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) and $WARNINGS warning(s) found.${NC}"
    echo -e "${RED}Please fix errors before deploying.${NC}"
    exit 1
fi
