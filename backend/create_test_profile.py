#!/usr/bin/env python3
"""
Script to create a test freelancer profile for testing job analysis
"""

from models.database import Database

def create_test_profile():
    """Create a test freelancer profile"""
    try:
        db = Database()
        
        # Create a test profile
        profile_id = db.add_freelancer_profile(
            name="Test Freelancer",
            email="test@example.com",
            hourly_rate=50.0,
            skills=["Python", "FastAPI", "React", "JavaScript", "SQL", "Docker"],
            experience_years=3,
            bio="Experienced full-stack developer with expertise in Python and React",
            portfolio_url="https://example.com/portfolio",
            github_url="https://github.com/testuser",
            linkedin_url="https://linkedin.com/in/testuser",
            timezone="UTC"
        )
        
        print(f"✅ Created test profile with ID: {profile_id}")
        
        # Verify the profile was created
        profile = db.get_freelancer_profile(profile_id)
        if profile:
            print(f"✅ Profile verified: {profile['name']}")
            print(f"   Skills: {profile['skills']}")
            print(f"   Hourly Rate: ${profile['hourly_rate']}")
            print(f"   Experience: {profile['experience_years']} years")
        else:
            print("❌ Failed to retrieve created profile")
            
        return profile_id
        
    except Exception as e:
        print(f"❌ Error creating test profile: {e}")
        return None

def main():
    print("Creating Test Freelancer Profile")
    print("=" * 40)
    
    profile_id = create_test_profile()
    
    if profile_id:
        print(f"\n🎉 Test profile created successfully!")
        print(f"   Profile ID: {profile_id}")
        print(f"   You can now use this ID for job analysis testing")
    else:
        print("\n❌ Failed to create test profile")

if __name__ == "__main__":
    main() 