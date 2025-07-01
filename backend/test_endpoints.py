#!/usr/bin/env python3
"""
Simple test script to verify backend endpoints are working
"""

import requests
import json

# Base URL for the backend
BASE_URL = "https://orion-freelancer-application.onrender.com"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\nTesting {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
        else:
            print("❌ FAILED")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("Testing Backend Endpoints")
    print("=" * 50)
    
    # Test basic endpoints
    test_endpoint("/")
    test_endpoint("/health")
    test_endpoint("/test")
    test_endpoint("/api/v1/test")
    test_endpoint("/api/v1/jobs/test")
    
    # Test profiles endpoint
    test_endpoint("/api/v1/profiles/")
    
    # Test jobs analyze endpoint with sample data
    sample_data = {
        "job_title": "Test Job",
        "job_description": "This is a test job description",
        "required_skills": ["Python", "FastAPI"],
        "client_rating": 4.5,
        "avg_pay_rate": 50.0,
        "job_url": "https://example.com",
        "freelancer_id": 1  # Use the profile ID from the deployed database
    }
    
    test_endpoint("/api/v1/jobs/analyze", method="POST", data=sample_data)

if __name__ == "__main__":
    main() 