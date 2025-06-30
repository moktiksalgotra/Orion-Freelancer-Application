from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import profiles, jobs, proposals, analytics
import os

app = FastAPI(
    title="Upwork Job Analyzer API",
    description="AI-powered job analysis and proposal generation for freelancers",
    version="1.0.0"
)

# Get allowed origins from environment variable or use defaults
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,http://localhost:3000,https://upwork-job-analyzer-frontend.onrender.com"
).split(",")

# Print allowed origins for debugging
print(f"Allowed CORS origins: {ALLOWED_ORIGINS}")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "ok", 
        "message": "Upwork Job Analyzer API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    print("Health check endpoint called")
    return {"status": "healthy"}

# Include all routers
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(proposals.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 