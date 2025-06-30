#!/bin/bash

# Deployment script for Upwork Job Analyzer
# This script helps prepare your application for deployment on Render

echo "🚀 Upwork Job Analyzer Deployment Helper"
echo "========================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    echo "   git remote add origin <your-repo-url>"
    echo "   git push -u origin main"
    exit 1
fi

# Check backend files
echo "📋 Checking backend configuration..."
if [ -f "backend/Procfile" ]; then
    echo "✅ Procfile found"
else
    echo "❌ Procfile missing in backend directory"
fi

if [ -f "backend/requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "❌ requirements.txt missing in backend directory"
fi

if [ -f "backend/render.yaml" ]; then
    echo "✅ render.yaml found"
else
    echo "❌ render.yaml missing in backend directory"
fi

# Check frontend files
echo "📋 Checking frontend configuration..."
if [ -f "frontend/package.json" ]; then
    echo "✅ package.json found"
else
    echo "❌ package.json missing in frontend directory"
fi

if [ -f "frontend/render.yaml" ]; then
    echo "✅ render.yaml found"
else
    echo "❌ render.yaml missing in frontend directory"
fi

echo ""
echo "📝 Next Steps:"
echo "1. Push your code to GitHub/GitLab"
echo "2. Go to https://dashboard.render.com"
echo "3. Deploy backend as Web Service"
echo "4. Deploy frontend as Static Site"
echo "5. Set environment variables in Render dashboard"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "🔧 Environment Variables to set in Render:"
echo ""
echo "Backend:"
echo "  GROQ_API_KEY=your_groq_api_key"
echo "  DATABASE_URL=your_database_url"
echo "  ALLOWED_ORIGINS=https://your-frontend-url.onrender.com"
echo ""
echo "Frontend:"
echo "  VITE_API_BASE_URL=https://your-backend-url.onrender.com/api/v1" 