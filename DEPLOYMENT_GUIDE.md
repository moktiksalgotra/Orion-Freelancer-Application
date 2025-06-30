# Deployment Guide for Upwork Job Analyzer

This guide explains how to deploy the backend and frontend separately on Render.

## Prerequisites

1. A Render account (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, etc.)
3. API keys for external services (GROQ API)

## Backend Deployment

### Step 1: Prepare Backend Repository

The backend is already configured with the necessary files:
- `Procfile` - Tells Render how to run the application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration

### Step 2: Deploy Backend on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Select the repository containing your backend code

3. **Configure the Service**:
   - **Name**: `upwork-job-analyzer-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend` (if your backend is in a subdirectory)

4. **Set Environment Variables**:
   - `GROQ_API_KEY`: Your GROQ API key
   - `DATABASE_URL`: Your database connection string (if using external database)
   - `ALLOWED_ORIGINS`: `https://upwork-job-analyzer-frontend.onrender.com` (update with your frontend URL)

5. **Deploy**: Click "Create Web Service"

### Step 3: Get Backend URL

After deployment, Render will provide a URL like:
`https://upwork-job-analyzer-backend.onrender.com`

## Frontend Deployment

### Step 1: Prepare Frontend Repository

The frontend is configured with:
- `render.yaml` - Render configuration
- `package.json` - Node.js dependencies and build scripts

### Step 2: Deploy Frontend on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Create New Static Site**:
   - Click "New +" → "Static Site"
   - Connect your Git repository
   - Select the repository containing your frontend code

3. **Configure the Service**:
   - **Name**: `upwork-job-analyzer-frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Root Directory**: `frontend` (if your frontend is in a subdirectory)

4. **Set Environment Variables**:
   - `VITE_API_BASE_URL`: `https://upwork-job-analyzer-backend.onrender.com/api/v1` (your backend URL)

5. **Deploy**: Click "Create Static Site"

### Step 3: Get Frontend URL

After deployment, Render will provide a URL like:
`https://upwork-job-analyzer-frontend.onrender.com`

## Environment Variables

### Backend Environment Variables

Set these in your Render backend service:

```bash
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=your_database_url_here
ALLOWED_ORIGINS=https://upwork-job-analyzer-frontend.onrender.com
```

### Frontend Environment Variables

Set these in your Render frontend service:

```bash
VITE_API_BASE_URL=https://upwork-job-analyzer-backend.onrender.com/api/v1
```

## Local Development

### Backend Development

1. Navigate to backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --reload`

### Frontend Development

1. Navigate to frontend directory: `cd frontend`
2. Create `.env` file with:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```
3. Install dependencies: `npm install`
4. Run the development server: `npm run dev`

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure `ALLOWED_ORIGINS` in backend includes your frontend URL
2. **API Connection Issues**: Verify `VITE_API_BASE_URL` points to your deployed backend
3. **Build Failures**: Check that all dependencies are properly listed in `requirements.txt` and `package.json`

### Checking Logs

- **Backend Logs**: Go to your backend service on Render → "Logs" tab
- **Frontend Logs**: Go to your frontend service on Render → "Logs" tab

### Health Checks

- Backend health: `https://your-backend-url.onrender.com/health`
- Frontend: Should load the React application

## Security Notes

1. Never commit API keys to your repository
2. Use environment variables for all sensitive configuration
3. Keep your dependencies updated
4. Monitor your Render usage (free tier has limits)

## Cost Considerations

- **Free Tier**: Both services can run on Render's free tier
- **Limits**: Free tier has monthly usage limits and may sleep after inactivity
- **Upgrade**: Consider upgrading to paid plans for production use 