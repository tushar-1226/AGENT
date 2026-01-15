#!/bin/bash

# Quick Deployment - Vercel + Render Setup
# This script helps you deploy F.R.I.D.A.Y. Agent to production

echo "========================================="
echo "  F.R.I.D.A.Y. Agent - Deployment Setup"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 Pre-Deployment Checklist:${NC}"
echo ""

# Check Git repository
if git remote -v | grep -q "github.com"; then
    REPO_URL=$(git remote get-url origin)
    echo -e "${GREEN}✓ Git repository connected:${NC}"
    echo "  $REPO_URL"
else
    echo -e "${YELLOW}⚠ Warning: No GitHub remote found${NC}"
fi
echo ""

# Check if changes are committed
if git diff-index --quiet HEAD --; then
    echo -e "${GREEN}✓ All changes committed${NC}"
else
    echo -e "${YELLOW}⚠ Warning: You have uncommitted changes${NC}"
    echo "  Run: git add . && git commit -m 'deployment preparation'"
fi
echo ""

# Check Vercel CLI
if command -v vercel &> /dev/null; then
    echo -e "${GREEN}✓ Vercel CLI installed${NC}"
else
    echo -e "${YELLOW}⚠ Vercel CLI not installed${NC}"
    echo "  Install: npm install -g vercel"
fi
echo ""

# Check environment files
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓ Backend .env file exists${NC}"
    if grep -q "GEMINI_API_KEY=AIza" backend/.env; then
        echo -e "${GREEN}  ✓ GEMINI_API_KEY configured${NC}"
    fi
    if grep -q "NEWS_API_KEY=60b37be7a8a74224bb6c0c68c2dcfa8a" backend/.env; then
        echo -e "${GREEN}  ✓ NEWS_API_KEY configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Backend .env file missing${NC}"
fi
echo ""

echo "========================================="
echo -e "${BLUE}📚 Deployment Instructions:${NC}"
echo "========================================="
echo ""
echo "BACKEND (Render):"
echo "  1. Go to: https://dashboard.render.com/"
echo "  2. Click 'New +' → 'Web Service'"
echo "  3. Connect GitHub: tushar-1226/AGENT"
echo "  4. Settings:"
echo "     - Name: friday-backend"
echo "     - Environment: Docker"
echo "     - Dockerfile: Dockerfile.backend"
echo "  5. Add environment variables (from backend/.env)"
echo "  6. Click 'Create Web Service'"
echo ""
echo "FRONTEND (Vercel):"
echo "  1. Install Vercel CLI:"
echo "     npm install -g vercel"
echo ""
echo "  2. Login to Vercel:"
echo "     vercel login"
echo ""
echo "  3. Deploy frontend:"
echo "     cd frontend"
echo "     vercel"
echo ""
echo "  4. After deployment, add backend URL:"
echo "     vercel env add NEXT_PUBLIC_API_URL production"
echo "     # Paste your Render backend URL"
echo ""
echo "  5. Deploy to production:"
echo "     vercel --prod"
echo ""
echo "========================================="
echo -e "${GREEN}✓ Ready to deploy!${NC}"
echo "========================================="
echo ""
echo "⚠️  IMPORTANT: Commit and push your changes first!"
echo "    git add ."
echo "    git commit -m 'Add deployment configuration'"
echo "    git push origin main"
echo ""
echo "📖 Full guide: See vercel_deployment_guide.md artifact"
echo ""
