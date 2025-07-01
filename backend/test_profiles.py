#!/usr/bin/env python3
"""
Script to test profiles endpoint and create a profile via API
"""

import requests
import json

# Base URL for the backend
BASE_URL = "https://orion-freelancer-application.onrender.com"

def test_profiles():
    """Test profiles endpoint"""
    url = f"{BASE_URL}/api/v1/profiles/"
    print(f"Testing GET {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            profiles = response.json()
            print(f"Found {len(profiles)} profiles")
            for profile in profiles:
                print(f"  - ID: {profile.get('id')}, Name: {profile.get('name')}")
            return profiles
        else:
            print("❌ FAILED")
            return []
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return []

def create_profile():
    """Create a profile via API"""
    url = f"{BASE_URL}/api/v1/profiles/"
    print(f"\nTesting POST {url}")
    
    profile_data = {
        "name": "Test Freelancer",
        "email": "test@example.com",
        "hourly_rate": 50.0,
        "skills": ["Python", "FastAPI", "React", "JavaScript", "SQL", "Docker"],
        "experience_years": 3,
        "bio": "Experienced full-stack developer with expertise in Python and React",
        "portfolio_url": "https://example.com/portfolio",
        "github_url": "https://github.com/testuser",
        "linkedin_url": "https://linkedin.com/in/testuser",
        "timezone": "UTC"
    }
    
    try:
        response = requests.post(url, json=profile_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Created profile with ID: {profile.get('id')}")
            return profile.get('id')
        else:
            print("❌ FAILED")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def main():
    print("Testing Profiles Endpoint")
    print("=" * 40)
    
    # First, check existing profiles
    profiles = test_profiles()
    
    # If no profiles exist, create one
    if not profiles:
        print("\nNo profiles found. Creating a test profile...")
        profile_id = create_profile()
        
        if profile_id:
            print(f"\n🎉 Profile created successfully!")
            print(f"   Profile ID: {profile_id}")
            print(f"   You can now use this ID for job analysis testing")
        else:
            print("\n❌ Failed to create profile")
    else:
        print(f"\nFound {len(profiles)} existing profiles")
        if profiles:
            profile_id = profiles[0].get('id')
            print(f"   Using profile ID: {profile_id}")

if __name__ == "__main__":
    main() 