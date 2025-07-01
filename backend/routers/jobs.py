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
    print("Received scrape request:", request)
    try:
        # Filter out empty or whitespace-only keywords
        valid_keywords = [k.strip() for k in request.keywords if k.strip()]
        if not valid_keywords:
            # If no valid keywords, use a generic keyword to fetch latest jobs
            valid_keywords = ["latest"]
            print("No valid keywords provided. Using default keyword: 'latest'")

        scraper = get_scraper()
        scraped_jobs = []
        added_count = 0
        
        print(f"Processing {len(valid_keywords)} keywords: {valid_keywords}")
        
        for keyword in valid_keywords:
            print(f"Searching for keyword: {keyword}")
            jobs = scraper.search_jobs(
                keywords=[keyword],
                max_jobs=request.max_jobs_per_keyword,
                category_filter=request.category_filter
            )
            print(f"Found {len(jobs)} jobs for keyword '{keyword}'")
            
            for job in jobs:
                job_id = db.add_scraped_job(
                    job_title=job.get('job_title', ''),
                    job_url=job.get('job_url', ''),
                    job_description=job.get('job_description', ''),
                    required_skills=job.get('required_skills', []),
                    client_name=job.get('client_name', ''),
                    client_rating=job.get('client_rating', 0.0),
                    client_total_jobs=job.get('client_total_jobs', 0),
                    client_total_hires=job.get('client_total_hires', 0),
                    client_avg_review=job.get('client_avg_review', 0.0),
                    budget_range=job.get('budget_range', ''),
                    avg_pay_rate=job.get('avg_pay_rate', 0.0),
                    project_duration=job.get('project_duration', ''),
                    job_category=job.get('job_category', ''),
                    posted_date=job.get('posted_date', '')
                )
                if job_id:
                    added_count += 1
                scraped_jobs.append(job)
        
        total_jobs = len(scraped_jobs)
        duplicate_count = total_jobs - added_count
        
        if total_jobs == 0:
            message = (f"No jobs found for the given keywords. Possible reasons: "
                       f"- No relevant jobs available at this time. "
                       f"- API may be rate limited or unavailable. "
                       f"- The keyword(s) may be too specific. "
                       f"Try different keywords or check your API settings.")
            print(message)
            return {"message": message, "jobs": [], "added_count": 0, "total_count": 0}
        
        message = f"Scraped {total_jobs} jobs"
        if duplicate_count > 0:
            message += f" ({added_count} new, {duplicate_count} duplicates ignored)"
        
        print(f"Final result: {message}")
        return {"message": message, "jobs": scraped_jobs, "added_count": added_count, "total_count": total_jobs}
    except Exception as e:
        print(f"Error in scrape_jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scraped")
async def get_scraped_jobs(limit: int = 50, db: Database = Depends(get_db)):
    """Get scraped jobs from database"""
    try:
        jobs = db.get_scraped_jobs(limit=limit)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/scraped")
async def clear_scraped_jobs(db: Database = Depends(get_db)):
    """Clear all scraped jobs from database"""
    try:
        success = db.clear_scraped_jobs()
        if success:
            return {"message": "All scraped jobs cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear scraped jobs")
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