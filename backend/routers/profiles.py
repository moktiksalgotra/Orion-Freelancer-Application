from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from models.database import Database
import json

router = APIRouter(prefix="/profiles", tags=["profiles"])

# Pydantic models for request/response
class ProfileCreate(BaseModel):
    name: str
    email: Optional[str] = None
    hourly_rate: float
    skills: List[str]
    experience_years: int
    bio: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    relevant_experience: Optional[str] = None
    timezone: Optional[str] = None

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    hourly_rate: Optional[float] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    relevant_experience: Optional[str] = None
    timezone: Optional[str] = None
    availability_status: Optional[str] = None

class ProfileResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    hourly_rate: float
    skills: List[str]
    experience_years: int
    bio: Optional[str]
    portfolio_url: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    relevant_experience: Optional[str]
    timezone: Optional[str]
    availability_status: str
    created_at: str
    updated_at: str

# Relevant Experience Project models
class RelevantExperienceProjectCreate(BaseModel):
    project_title: str
    project_description: str
    project_url: Optional[str] = None
    company_name: Optional[str] = None
    project_type: Optional[str] = None
    technologies_used: Optional[List[str]] = None
    key_achievements: Optional[str] = None
    project_duration: Optional[str] = None
    completion_date: Optional[str] = None

class RelevantExperienceProjectUpdate(BaseModel):
    project_title: Optional[str] = None
    project_description: Optional[str] = None
    project_url: Optional[str] = None
    company_name: Optional[str] = None
    project_type: Optional[str] = None
    technologies_used: Optional[List[str]] = None
    key_achievements: Optional[str] = None
    project_duration: Optional[str] = None
    completion_date: Optional[str] = None

class RelevantExperienceProjectResponse(BaseModel):
    id: int
    freelancer_id: int
    project_title: str
    project_description: str
    project_url: Optional[str]
    company_name: Optional[str]
    project_type: Optional[str]
    technologies_used: Optional[List[str]]
    key_achievements: Optional[str]
    project_duration: Optional[str]
    completion_date: Optional[str]
    created_at: str

# Dependency to get database instance
def get_db():
    return Database()

@router.post("/", response_model=ProfileResponse)
async def create_profile(profile: ProfileCreate, db: Database = Depends(get_db)):
    """Create a new freelancer profile"""
    try:
        profile_id = db.add_freelancer_profile(
            name=profile.name,
            email=profile.email,
            hourly_rate=profile.hourly_rate,
            skills=profile.skills,
            experience_years=profile.experience_years,
            bio=profile.bio,
            portfolio_url=profile.portfolio_url,
            github_url=profile.github_url,
            linkedin_url=profile.linkedin_url,
            relevant_experience=profile.relevant_experience,
            timezone=profile.timezone
        )
        
        # Get the created profile
        created_profile = db.get_freelancer_profile(profile_id)
        if not created_profile:
            raise HTTPException(status_code=500, detail="Failed to create profile")
        
        return ProfileResponse(**created_profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ProfileResponse])
async def get_all_profiles(db: Database = Depends(get_db)):
    """Get all freelancer profiles"""
    try:
        print("DEBUG: Starting get_all_profiles")
        profiles = db.get_all_freelancer_profiles()
        print(f"DEBUG: Retrieved {len(profiles)} profiles from database")
        
        # Convert each profile to ProfileResponse with error handling
        response_profiles = []
        for i, profile in enumerate(profiles):
            try:
                print(f"DEBUG: Processing profile {i}: {profile.get('name', 'Unknown')}")
                response_profile = ProfileResponse(**profile)
                response_profiles.append(response_profile)
            except Exception as profile_error:
                print(f"ERROR processing profile {i}: {profile_error}")
                print(f"Profile data: {profile}")
                raise profile_error
        
        print(f"DEBUG: Successfully created {len(response_profiles)} ProfileResponse objects")
        return response_profiles
    except Exception as e:
        import traceback
        print(f"ERROR in get_all_profiles: {e} ({type(e)})")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: Database = Depends(get_db)):
    """Get a specific freelancer profile"""
    try:
        profile = db.get_freelancer_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return ProfileResponse(**profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: int, profile_update: ProfileUpdate, db: Database = Depends(get_db)):
    """Update a freelancer profile"""
    try:
        # Check if profile exists
        existing_profile = db.get_freelancer_profile(profile_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Prepare update data
        update_data = {}
        for field, value in profile_update.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update profile
        success = db.update_freelancer_profile(profile_id, **update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        # Get updated profile
        updated_profile = db.get_freelancer_profile(profile_id)
        if not updated_profile:
            print(f"[ERROR] Updated profile not found for id {profile_id} after update.")
            raise HTTPException(status_code=500, detail="Failed to fetch updated profile")
        return ProfileResponse(**updated_profile)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{profile_id}")
async def delete_profile(profile_id: int, db: Database = Depends(get_db)):
    """Delete a freelancer profile and all related data"""
    try:
        # Check if profile exists
        existing_profile = db.get_freelancer_profile(profile_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Delete only the specific profile and related data
        success = db.delete_freelancer_profile(profile_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete profile")
        
        return {"message": "Profile deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Relevant Experience Project endpoints
@router.post("/{profile_id}/relevant-experience", response_model=RelevantExperienceProjectResponse)
async def add_relevant_experience_project(
    profile_id: int, 
    project: RelevantExperienceProjectCreate, 
    db: Database = Depends(get_db)
):
    """Add a relevant experience project to a freelancer profile"""
    try:
        # Check if profile exists
        existing_profile = db.get_freelancer_profile(profile_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Add the project
        project_id = db.add_relevant_experience_project(
            freelancer_id=profile_id,
            project_title=project.project_title,
            project_description=project.project_description,
            project_url=project.project_url,
            company_name=project.company_name,
            project_type=project.project_type,
            technologies_used=project.technologies_used,
            key_achievements=project.key_achievements,
            project_duration=project.project_duration,
            completion_date=project.completion_date
        )
        
        if not project_id:
            raise HTTPException(status_code=500, detail="Failed to add relevant experience project")
        
        # Get the added project
        projects = db.get_relevant_experience_projects(profile_id)
        for proj in projects:
            if proj['id'] == project_id:
                return RelevantExperienceProjectResponse(**proj)
        
        raise HTTPException(status_code=500, detail="Failed to retrieve added project")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{profile_id}/relevant-experience", response_model=List[RelevantExperienceProjectResponse])
async def get_relevant_experience_projects(profile_id: int, db: Database = Depends(get_db)):
    """Get all relevant experience projects for a freelancer profile"""
    try:
        # Check if profile exists
        existing_profile = db.get_freelancer_profile(profile_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        projects = db.get_relevant_experience_projects(profile_id)
        return [RelevantExperienceProjectResponse(**project) for project in projects]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{profile_id}/relevant-experience/{project_id}", response_model=RelevantExperienceProjectResponse)
async def update_relevant_experience_project(
    profile_id: int,
    project_id: int,
    project_update: RelevantExperienceProjectUpdate,
    db: Database = Depends(get_db)
):
    """Update a relevant experience project"""
    try:
        # Check if profile exists
        existing_profile = db.get_freelancer_profile(profile_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Prepare update data
        update_data = {}
        for field, value in project_update.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update the project
        success = db.update_relevant_experience_project(project_id, **update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update project")
        
        # Get the updated project
        projects = db.get_relevant_experience_projects(profile_id)
        for proj in projects:
            if proj['id'] == project_id:
                return RelevantExperienceProjectResponse(**proj)
        
        raise HTTPException(status_code=404, detail="Updated project not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{profile_id}/relevant-experience/{project_id}")
async def delete_relevant_experience_project(profile_id: int, project_id: int, db: Database = Depends(get_db)):
    """Delete a relevant experience project"""
    try:
        # Check if profile exists
        existing_profile = db.get_freelancer_profile(profile_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Delete the project
        success = db.delete_relevant_experience_project(project_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete project")
        
        return {"message": "Relevant experience project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 