#!/bin/bash

# F.R.I.D.A.Y. Agent - Production Deployment Script
# This script builds and starts the application using Docker Compose

set -e  # Exit on error

echo "========================================="
echo "  F.R.I.D.A.Y. Agent Deployment Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}ERROR: backend/.env file not found!${NC}"
    echo ""
    echo "Please create backend/.env with your configuration:"
    echo "  cp backend/.env.example backend/.env"
    echo "  # Then edit backend/.env with your API keys"
    echo ""
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=AIza" backend/.env; then
    echo -e "${YELLOW}WARNING: GEMINI_API_KEY may not be set properly in backend/.env${NC}"
    echo "The application requires a valid Gemini API key to function."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create frontend .env.local if it doesn't exist
if [ ! -f "frontend/.env.local" ]; then
    echo -e "${YELLOW}Creating frontend/.env.local...${NC}"
    cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo -e "${GREEN}✓ Created frontend/.env.local${NC}"
fi

# Stop existing containers
echo ""
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build images
echo ""
echo "Building Docker images..."
echo "This may take a few minutes on first run..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Docker build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build completed successfully${NC}"

# Start containers
echo ""
echo "Starting containers..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check backend health
echo "Checking backend health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}ERROR: Backend failed to start${NC}"
        echo "Check logs with: docker-compose logs backend"
        exit 1
    fi
    echo "Waiting for backend... ($i/30)"
    sleep 2
done

# Check frontend
echo "Checking frontend..."
for i in {1..30}; do
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}ERROR: Frontend failed to start${NC}"
        echo "Check logs with: docker-compose logs frontend"
        exit 1
    fi
    echo "Waiting for frontend... ($i/30)"
    sleep 2
done

# Success
echo ""
echo "========================================="
echo -e "${GREEN}✓ F.R.I.D.A.Y. Agent is now running!${NC}"
echo "========================================="
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📊 View logs:"
echo "  docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "  docker-compose down"
echo ""
echo "📝 Check status:"
echo "  docker-compose ps"
echo ""
