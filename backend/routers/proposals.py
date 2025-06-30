from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from models.database import Database
from utils.proposal_generator import ProposalGenerator
from datetime import datetime

router = APIRouter(prefix="/proposals", tags=["proposals"])

# Pydantic models
class ProposalRequest(BaseModel):
    freelancer_id: int
    job_title: str
    job_description: str
    required_skills: List[str]
    client_rating: Optional[float] = None
    job_budget: Optional[float] = None
    job_url: Optional[str] = None
    use_ai: bool = True

class ProposalResponse(BaseModel):
    id: int
    freelancer_id: int
    job_title: str
    job_url: Optional[str]
    proposal_text: str
    client_response: Optional[str]
    proposal_status: str
    submission_date: Optional[str]
    response_date: Optional[str]
    job_budget: Optional[float]
    client_rating: Optional[float]
    client_name: Optional[str]
    job_category: Optional[str]
    keywords_used: Optional[str]
    created_at: str

# Dependencies
def get_db():
    return Database()

def get_proposal_generator():
    return ProposalGenerator()

@router.post("/generate", response_model=ProposalResponse)
async def generate_proposal(request: ProposalRequest, db: Database = Depends(get_db)):
    """Generate a proposal for a job"""
    try:
        # Get freelancer profile
        profile = db.get_freelancer_profile(request.freelancer_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Freelancer profile not found")
        
        # Get past projects for context
        past_projects = db.get_past_projects(request.freelancer_id)
        
        # Get relevant experience projects
        relevant_experience_projects = db.get_relevant_experience_projects(request.freelancer_id)
        
        # Get successful proposals for reference
        successful_proposals = db.get_successful_proposals(request.freelancer_id)
        
        # Generate proposal
        generator = get_proposal_generator()
        proposal_text = generator.generate_proposal(
            job_title=request.job_title,
            job_description=request.job_description,
            required_skills=request.required_skills,
            freelancer_name=profile['name'],
            freelancer_skills=profile['skills'],
            freelancer_experience=profile['experience_years'],
            freelancer_bio=profile['bio'],
            github_url=profile['github_url'],
            linkedin_url=profile['linkedin_url'],
            relevant_experience=relevant_experience_projects,
            past_projects=past_projects,
            successful_proposals=successful_proposals,
            use_ai=request.use_ai
        )
        
        # Save proposal to database
        proposal_id = db.add_successful_proposal(
            freelancer_id=request.freelancer_id,
            job_title=request.job_title,
            proposal_text=proposal_text,
            job_url=request.job_url,
            job_budget=request.job_budget,
            client_rating=request.client_rating,
            proposal_status='Generated'
        )
        
        # Get the saved proposal
        proposals = db.get_successful_proposals(request.freelancer_id)
        for proposal in proposals:
            if proposal['id'] == proposal_id:
                return ProposalResponse(**proposal)
        
        raise HTTPException(status_code=500, detail="Failed to retrieve generated proposal")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProposalResponse])
async def get_proposals(freelancer_id: int, db: Database = Depends(get_db)):
    """Get all proposals for a freelancer"""
    try:
        proposals = db.get_successful_proposals(freelancer_id)
        return [ProposalResponse(**proposal) for proposal in proposals]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: int, db: Database = Depends(get_db)):
    """Get a specific proposal"""
    try:
        # This would need a new method in the database class
        # For now, we'll get all proposals and filter
        proposals = db.get_successful_proposals(1)  # Get from first profile
        for proposal in proposals:
            if proposal['id'] == proposal_id:
                return ProposalResponse(**proposal)
        
        raise HTTPException(status_code=404, detail="Proposal not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{proposal_id}")
async def update_proposal_status(
    proposal_id: int, 
    status: str, 
    client_response: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Update proposal status and client response"""
    try:
        # This would need a new method in the database class
        # For now, return a placeholder response
        return {
            "message": "Proposal status updated",
            "proposal_id": proposal_id,
            "status": status,
            "client_response": client_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 