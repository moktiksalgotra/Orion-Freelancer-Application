from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from models.database import Database
from utils.web_scraper import UpworkScraper
from utils.job_analyzer import JobAnalyzer
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Pydantic models
class ScrapingRequest(BaseModel):
    keywords: List[str]
    max_jobs_per_keyword: int = 10
    category_filter: Optional[str] = None

class JobAnalysisRequest(BaseModel):
    job_title: str
    job_description: str
    required_skills: List[str]
    client_rating: Optional[float] = None
    avg_pay_rate: Optional[float] = None
    job_url: Optional[str] = None
    freelancer_id: int

# Dependencies
def get_db():
    return Database()

def get_scraper():
    return UpworkScraper()

def get_analyzer():
    return JobAnalyzer()

@router.post("/scrape")
async def scrape_jobs(request: ScrapingRequest, db: Database = Depends(get_db)):
    """Scrape jobs from Upwork based on keywords"""
    try:
        scraper = get_scraper()
        scraped_jobs = []
        
        for keyword in request.keywords:
            jobs = scraper.search_jobs(
                keyword=keyword,
                max_jobs=request.max_jobs_per_keyword,
                category_filter=request.category_filter
            )
            
            for job in jobs:
                job_id = db.add_scraped_job(
                    job_title=job.get('title', ''),
                    job_url=job.get('url', ''),
                    job_description=job.get('description', ''),
                    required_skills=job.get('skills', []),
                    client_name=job.get('client_name', ''),
                    client_rating=job.get('client_rating', 0.0),
                    client_total_jobs=job.get('client_total_jobs', 0),
                    client_total_hires=job.get('client_total_hires', 0),
                    client_avg_review=job.get('client_avg_review', 0.0),
                    budget_range=job.get('budget_range', ''),
                    avg_pay_rate=job.get('avg_pay_rate', 0.0),
                    project_duration=job.get('project_duration', ''),
                    job_category=job.get('category', ''),
                    posted_date=job.get('posted_date', '')
                )
                scraped_jobs.append(job)
        
        return {"message": f"Scraped {len(scraped_jobs)} jobs", "jobs": scraped_jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scraped")
async def get_scraped_jobs(limit: int = 50, db: Database = Depends(get_db)):
    """Get scraped jobs from database"""
    try:
        jobs = db.get_scraped_jobs(limit=limit)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_job(request: JobAnalysisRequest, db: Database = Depends(get_db)):
    """Analyze a job for fit and generate recommendations"""
    try:
        profile = db.get_freelancer_profile(request.freelancer_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Freelancer profile not found")
        
        analyzer = get_analyzer()
        analysis_result = analyzer.analyze_job_fit(
            job_title=request.job_title,
            job_description=request.job_description,
            required_skills=request.required_skills,
            client_rating=request.client_rating,
            avg_pay_rate=request.avg_pay_rate,
            freelancer_skills=profile['skills'],
            freelancer_hourly_rate=profile['hourly_rate'],
            freelancer_experience=profile['experience_years']
        )
        
        analysis_id = db.add_job_analysis(
            freelancer_id=request.freelancer_id,
            job_title=request.job_title,
            job_url=request.job_url,
            job_description=request.job_description,
            required_skills=request.required_skills,
            client_rating=request.client_rating,
            avg_pay_rate=request.avg_pay_rate,
            analysis_result=analysis_result['result'],
            analysis_reasons=analysis_result['reasons'],
            recommendation=analysis_result['recommendation']
        )
        
        return {
            "id": analysis_id,
            "analysis": analysis_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scrape-url")
async def scrape_job_from_url(url: str):
    """Scrape a specific job from URL"""
    try:
        scraper = get_scraper()
        job_data = scraper.scrape_job_from_url(url)
        if not job_data:
            raise HTTPException(status_code=404, detail="Could not scrape job from URL")
        return job_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

