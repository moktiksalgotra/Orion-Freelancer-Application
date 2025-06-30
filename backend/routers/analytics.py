from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from models.database import Database
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Pydantic models
class DashboardStats(BaseModel):
    total_profiles: int
    total_jobs_scraped: int
    total_jobs_analyzed: int
    total_proposals_generated: int
    recent_jobs: List[Dict[str, Any]]
    recent_proposals: List[Dict[str, Any]]

class JobAnalysisHistory(BaseModel):
    id: int
    freelancer_id: int
    job_title: str
    job_url: Optional[str]
    job_description: str
    required_skills: List[str]
    client_rating: Optional[float]
    avg_pay_rate: Optional[float]
    analysis_result: str
    analysis_reasons: str
    recommendation: str
    analyzed_at: str

# Dependencies
def get_db():
    return Database()

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: Database = Depends(get_db)):
    """Get dashboard statistics and recent data"""
    try:
        # Get all profiles
        profiles = db.get_all_freelancer_profiles()
        total_profiles = len(profiles)
        
        # Get scraped jobs
        scraped_jobs = db.get_scraped_jobs(limit=1000)  # Get all for counting
        total_jobs_scraped = len(scraped_jobs)
        
        # Get recent jobs (last 10)
        recent_jobs = scraped_jobs[:10] if scraped_jobs else []
        
        # Get proposals (we'll need to get from all profiles)
        total_proposals = 0
        recent_proposals = []
        
        for profile in profiles:
            proposals = db.get_successful_proposals(profile['id'])
            total_proposals += len(proposals)
            recent_proposals.extend(proposals[:5])  # Get 5 most recent from each profile
        
        # Sort recent proposals by date and take top 10
        recent_proposals.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        recent_proposals = recent_proposals[:10]
        
        # For job analysis history, we'll need to implement a method to get all
        # For now, we'll estimate based on profiles
        total_jobs_analyzed = total_profiles * 5  # Estimate
        
        return DashboardStats(
            total_profiles=total_profiles,
            total_jobs_scraped=total_jobs_scraped,
            total_jobs_analyzed=total_jobs_analyzed,
            total_proposals_generated=total_proposals,
            recent_jobs=recent_jobs,
            recent_proposals=recent_proposals
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles/{profile_id}/stats")
async def get_profile_stats(profile_id: int, db: Database = Depends(get_db)):
    """Get statistics for a specific profile"""
    try:
        profile = db.get_freelancer_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get past projects
        past_projects = db.get_past_projects(profile_id)
        
        # Get proposals
        proposals = db.get_successful_proposals(profile_id)
        
        # Calculate some basic stats
        total_projects = len(past_projects)
        total_proposals = len(proposals)
        
        # Calculate average project rating
        avg_project_rating = 0
        if past_projects:
            ratings = [p.get('project_rating', 0) for p in past_projects if p.get('project_rating')]
            avg_project_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Calculate total earnings (estimate)
        total_earnings = 0
        for project in past_projects:
            if project.get('project_budget'):
                total_earnings += project['project_budget']
        
        return {
            "profile": profile,
            "stats": {
                "total_projects": total_projects,
                "total_proposals": total_proposals,
                "avg_project_rating": avg_project_rating,
                "total_earnings": total_earnings,
                "experience_years": profile['experience_years']
            },
            "recent_projects": past_projects[:5],
            "recent_proposals": proposals[:5]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/trends")
async def get_job_trends(db: Database = Depends(get_db)):
    """Get job market trends and insights"""
    try:
        scraped_jobs = db.get_scraped_jobs(limit=1000)
        
        if not scraped_jobs:
            return {"message": "No job data available for trends"}
        
        # Analyze job categories
        categories = {}
        for job in scraped_jobs:
            category = job.get('job_category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        # Analyze pay rates
        pay_rates = [job.get('avg_pay_rate', 0) for job in scraped_jobs if job.get('avg_pay_rate')]
        avg_pay_rate = sum(pay_rates) / len(pay_rates) if pay_rates else 0
        
        # Analyze client ratings
        client_ratings = [job.get('client_rating', 0) for job in scraped_jobs if job.get('client_rating')]
        avg_client_rating = sum(client_ratings) / len(client_ratings) if client_ratings else 0
        
        # Get most common skills
        all_skills = []
        for job in scraped_jobs:
            skills = job.get('required_skills', [])
            if isinstance(skills, list):
                all_skills.extend(skills)
        
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Get top 10 skills
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_jobs_analyzed": len(scraped_jobs),
            "job_categories": categories,
            "avg_pay_rate": avg_pay_rate,
            "avg_client_rating": avg_client_rating,
            "top_skills": top_skills,
            "recent_jobs_count": len([j for j in scraped_jobs if j.get('scraped_at')])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/{profile_id}")
async def export_profile_data(profile_id: int, db: Database = Depends(get_db)):
    """Export all data for a profile"""
    try:
        profile = db.get_freelancer_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        past_projects = db.get_past_projects(profile_id)
        proposals = db.get_successful_proposals(profile_id)
        
        return {
            "profile": profile,
            "past_projects": past_projects,
            "proposals": proposals,
            "export_date": datetime.now().isoformat(),
            "total_projects": len(past_projects),
            "total_proposals": len(proposals)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 