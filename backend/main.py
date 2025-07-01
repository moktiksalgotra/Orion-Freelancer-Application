from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import profiles, jobs, proposals, analytics

app = FastAPI(
    title="Upwork Job Analyzer API",
    description="AI-powered job analysis and proposal generation for freelancers",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    return {"status": "healthy"}

# Include all routers
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(proposals.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 