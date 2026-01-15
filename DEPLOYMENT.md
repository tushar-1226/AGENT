# F.R.I.D.A.Y. Agent - Deployment Guide

Complete guide for deploying the F.R.I.D.A.Y. Agent application to production.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Environment Configuration](#environment-configuration)
- [Local Docker Deployment](#local-docker-deployment)
- [Cloud Deployment Options](#cloud-deployment-options)
- [Production Best Practices](#production-best-practices)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

---

## Prerequisites

### Required
- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Git** for cloning the repository
- **Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Optional
- Domain name (for production deployment)
- SSL/TLS certificates
- Cloud platform account (Railway, Render, AWS, etc.)

---

## Quick Start with Docker

The fastest way to get F.R.I.D.A.Y. Agent running:

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd friday-agent

# 2. Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# 3. Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

That's it! The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## Environment Configuration

### Backend Environment Variables

Create `backend/.env` with the following configuration:

```bash
# REQUIRED - Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# OPTIONAL - External APIs
OPENWEATHER_API_KEY=your_weather_key          # For weather features (OpenWeatherMap)
NEWS_API_KEY=your_news_key                    # For news features (NewsAPI.org)
OPENROUTER_API_KEY=your_openrouter_key        # Alternative AI provider

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000            # Update for production

# LLM Configuration
LLM_MODE=cloud                                # Options: cloud, local, hybrid
LOCAL_MODEL=llama3.2:3b                       # If using local Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Multi-Model Configuration
ENABLE_MULTI_MODEL=false
USE_OPENROUTER_FALLBACK=true
```

**API Key Setup:**
- **Gemini API**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey) (Required)
- **NewsAPI.org**: Get from [NewsAPI.org](https://newsapi.org/register) (Optional - for news features)
- **OpenWeather**: Get from [OpenWeatherMap](https://openweathermap.org/api) (Optional - for weather features)

**Testing API Integration:**
```bash
# Test NewsAPI.org integration
cd backend
./venv/bin/python test_newsapi.py

# Should show: ✅ SUCCESS! NewsAPI.org is working correctly


### Frontend Environment Variables

Create `frontend/.env.local`:

```bash
# Local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# Docker deployment (use container name)
# NEXT_PUBLIC_API_URL=http://backend:8000

# Production deployment
# NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

---

## Local Docker Deployment

### Manual Docker Commands

If you prefer manual control over the deployment script:

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down
```

### Health Checks

Verify services are running:

```bash
# Backend health
curl http://localhost:8000/health

# Backend readiness
curl http://localhost:8000/ready

# Frontend
curl http://localhost:3000
```

---

## Cloud Deployment Options

### Option 1: Railway (Recommended - Full Stack)

Railway supports Docker and makes deployment simple:

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Initialize**:
   ```bash
   railway login
   railway init
   ```

3. **Configure Environment Variables**:
   - Go to Railway dashboard
   - Add all env vars from `backend/.env`
   - Set `FRONTEND_URL` to your Railway frontend URL

4. **Deploy**:
   ```bash
   railway up
   ```

**Cost**: Free tier available, ~$5-10/month for production

---

### Option 2: Render + Vercel

Split deployment: Backend on Render, Frontend on Vercel

#### Backend on Render:

1. Create new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `docker build -f Dockerfile.backend -t backend .`
   - **Start Command**: Docker will auto-detect
   - **Environment**: Add all backend env vars
4. Deploy

#### Frontend on Vercel:

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Deploy frontend:
   ```bash
   cd frontend
   vercel
   ```

3. Set environment variable:
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   # Enter your Render backend URL
   ```

**Cost**: Render free tier + Vercel free tier

---

### Option 3: AWS ECS/Fargate

For enterprise-grade deployment:

1. **Push images to ECR**:
   ```bash
   # Build and tag
   docker build -f Dockerfile.backend -t friday-backend .
   docker build -f Dockerfile.frontend -t friday-frontend .
   
   # Tag and push to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag friday-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/friday-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/friday-backend:latest
   ```

2. **Create ECS Task Definition** using the pushed images
3. **Create ECS Service** with Application Load Balancer
4. **Configure environment variables** in task definition

**Cost**: ~$30-50/month minimum

---

### Option 4: Google Cloud Run

Serverless container deployment:

```bash
# Backend
gcloud run deploy friday-backend \
  --source backend/ \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Frontend
gcloud run deploy friday-frontend \
  --source frontend/ \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Cost**: Pay-per-use, generous free tier

---

### Option 5: DigitalOcean App Platform

1. Create new **App** on [DigitalOcean](https://cloud.digitalocean.com/apps)
2. Connect GitHub repository
3. Detectsa Docker Compose automatically
4. Configure environment variables
5. Deploy

**Cost**: $5-12/month

---

## Production Best Practices

### Security Checklist

- [ ] **Never commit `.env` files** to Git
- [ ] Use **different API keys** for production vs development
- [ ] Enable **HTTPS/SSL** with valid certificates
- [ ] Configure **CORS** to allow only your production domain:
  ```python
  # In backend/app/main.py
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://yourdomain.com"],  # Not "*"
      ...
  )
  ```
- [ ] Set up **database backups** (see Maintenance section)
- [ ] Implement **rate limiting** for API endpoints
- [ ] Use **strong passwords** for any authentication
- [ ] Keep **dependencies updated** regularly

### Performance Optimization

1. **Enable caching** in production
2. **Use CDN** for static assets (Cloudflare, AWS CloudFront)
3. **Monitor resource usage**:
   ```bash
   docker stats
   ```
4. **Set resource limits** in docker-compose.yml:
   ```yaml
   backend:
     deploy:
       resources:
         limits:
           cpus: '1'
           memory: 1G
   ```

### Monitoring

1. **Health Checks**:
   - Backend: `https://your-domain.com/health`
   - Frontend: `https://your-domain.com`

2. **Logs**:
   ```bash
   # View logs
   docker-compose logs -f backend
   docker-compose logs -f frontend
   
   # Export logs
   docker-compose logs > deployment.log
   ```

3. **Use monitoring tools**:
   - **Uptime monitoring**: UptimeRobot, Pingdom
   - **Error tracking**: Sentry
   - **Performance**: New Relic, DataDog

---

## Troubleshooting

### Backend won't start

**Symptom**: Backend container exits immediately

**Solutions**:
1. Check logs:
   ```bash
   docker-compose logs backend
   ```
2. Verify `GEMINI_API_KEY` is set correctly
3. Ensure all required environment variables are present
4. Check database file permissions

### Frontend can't connect to backend

**Symptom**: API calls fail with network errors

**Solutions**:
1. Verify `NEXT_PUBLIC_API_URL` is correct
2. Check CORS configuration in backend
3. Ensure backend is healthy: `curl http://backend-url/health`
4. Check network connectivity between containers

### Database errors

**Symptom**: "Database is locked" or "Cannot open database"

**Solutions**:
1. Stop all containers: `docker-compose down`
2. Check file permissions on `*.db` files
3. Ensure volume mounts are correct
4. Restart with: `docker-compose up -d`

### OutMemory / Performance issues

**Solutions**:
1. Increase Docker memory limit
2. Set resource constraints in docker-compose.yml
3. Reduce concurrent requests
4. Enable caching

### Port already in use

**Symptom**: "Port 3000/8000 is already allocated"

**Solutions**:
```bash
# Find and kill process using port
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Or change ports in docker-compose.yml
```

---

## Maintenance

### Database Backups

Regular backups of SQLite databases:

```bash
# Create backup script: scripts/backup.sh
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

docker cp friday-backend:/app/users.db $BACKUP_DIR/
docker cp friday-backend:/app/chat_sessions.db $BACKUP_DIR/
docker cp friday-backend:/app/projects.db $BACKUP_DIR/
docker cp friday-backend:/app/tasks.db $BACKUP_DIR/
docker cp friday-backend:/app/analytics.db $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

Run daily with cron:
```bash
0 2 * * * /path/to/scripts/backup.sh
```

### Updates and Upgrades

```bash
# Stop services
docker-compose down

# Pull latest code
git pull origin main

# Rebuild images
docker-compose build --no-cache

# Start services
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

### Scaling

For increased traffic, use Docker Swarm or Kubernetes:

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml friday-stack

# Scale services
docker service scale friday-stack_backend=3
docker service scale friday-stack_frontend=3
```

---

## Additional Resources

- **API Documentation**: Visit `/docs` endpoint on your backend
- **README**: See [README.md](./README.md) for feature overview
- **GitHub Issues**: Report bugs and request features
- **Community**: Join discussions and get support

---

## Support

For deployment issues:
1. Check this guide thoroughly
2. Review logs: `docker-compose logs`
3. Test health endpoints
4. Open GitHub issue with:
   - Error messages
   - Environment details
   - Steps to reproduce

---

**Happy Deploying! 🚀**

Built with ❤️ for developers
