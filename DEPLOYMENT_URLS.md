# Deployment URLs Reference

## Backend Deployment
- **Service Type**: Web Service
- **URL**: `https://upwork-job-analyzer-backend.onrender.com`
- **API Base**: `https://upwork-job-analyzer-backend.onrender.com/api/v1`
- **Health Check**: `https://upwork-job-analyzer-backend.onrender.com/health`
- **API Docs**: `https://upwork-job-analyzer-backend.onrender.com/docs`

## Frontend Deployment
- **Service Type**: Static Site
- **URL**: `https://upwork-job-analyzer-frontend.onrender.com`

## Environment Variables

### Backend (Web Service)
```bash
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=your_database_url_here
ALLOWED_ORIGINS=https://upwork-job-analyzer-frontend.onrender.com
```

### Frontend (Static Site)
```bash
VITE_API_BASE_URL=https://upwork-job-analyzer-backend.onrender.com/api/v1
```

## Quick Commands

### Check Backend Health
```bash
curl https://upwork-job-analyzer-backend.onrender.com/health
```

### Test API Endpoint
```bash
curl https://upwork-job-analyzer-backend.onrender.com/api/v1/profiles/
```

## Render Dashboard Links
- **Backend Service**: https://dashboard.render.com/web/upwork-job-analyzer-backend
- **Frontend Service**: https://dashboard.render.com/static/upwork-job-analyzer-frontend

## Local Development URLs
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173 