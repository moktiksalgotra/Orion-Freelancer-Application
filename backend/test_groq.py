#!/usr/bin/env python3
"""
Test script for Groq API integration
Run this script to verify that your Groq API key is working correctly.
"""

import os
from dotenv import load_dotenv
from utils.proposal_generator import ProposalGenerator

def test_groq_integration():
    """Test the Groq API integration"""
    print("🧪 Testing Groq API Integration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Please set your Groq API key:")
        print("1. Copy backend/env.example to backend/.env")
        print("2. Edit .env and add your API key")
        print("3. Or set the environment variable directly")
        return False
    
    if api_key == "your_groq_api_key_here":
        print("❌ Please replace the placeholder API key with your actual Groq API key")
        return False
    
    print(f"✅ GROQ_API_KEY found: {api_key[:10]}...")
    
    # Test proposal generator initialization
    try:
        generator = ProposalGenerator()
        print(f"✅ Proposal generator initialized successfully")
        print(f"   AI enabled: {generator.use_ai}")
        
        if not generator.use_ai:
            print("❌ AI is not enabled. Check the error messages above.")
            return False
        
    except Exception as e:
        print(f"❌ Failed to initialize proposal generator: {e}")
        return False
    
    # Test AI proposal generation
    print("\n📝 Testing AI proposal generation...")
    try:
        test_proposal = generator.generate_proposal(
            job_title="Full-Stack Web Developer",
            job_description="We need a skilled developer to build a modern e-commerce platform with React frontend and Node.js backend. The project includes user authentication, payment processing, and admin dashboard.",
            required_skills=["React", "Node.js", "MongoDB", "JavaScript"],
            freelancer_name="John Doe",
            freelancer_skills=["React", "Node.js", "MongoDB", "JavaScript", "TypeScript", "Express"],
            freelancer_experience=5,
            freelancer_bio="Experienced full-stack developer with 5+ years building scalable web applications.",
            github_url="https://github.com/johndoe",
            linkedin_url="https://linkedin.com/in/johndoe",
            use_ai=True
        )
        
        if test_proposal and len(test_proposal) > 100:
            print("✅ AI proposal generation successful!")
            print(f"   Proposal length: {len(test_proposal)} characters")
            print("\n📄 Sample of generated proposal:")
            print("-" * 40)
            print(test_proposal[:500] + "...")
            print("-" * 40)
            return True
        else:
            print("❌ Generated proposal is too short or empty")
            return False
            
    except Exception as e:
        print(f"❌ AI proposal generation failed: {e}")
        return False

def test_template_fallback():
    """Test template-based proposal generation as fallback"""
    print("\n🔄 Testing template-based fallback...")
    
    try:
        generator = ProposalGenerator()
        test_proposal = generator.generate_proposal(
            job_title="Python Developer",
            job_description="Looking for a Python developer to build a data analysis tool.",
            required_skills=["Python", "Pandas", "NumPy"],
            freelancer_name="Jane Smith",
            freelancer_skills=["Python", "Pandas", "NumPy", "Matplotlib"],
            freelancer_experience=3,
            use_ai=False
        )
        
        if test_proposal and len(test_proposal) > 100:
            print("✅ Template-based proposal generation successful!")
            print(f"   Proposal length: {len(test_proposal)} characters")
            return True
        else:
            print("❌ Template-based proposal generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Template-based proposal generation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Orion Freelancer Application - Groq API Test")
    print("=" * 60)
    
    # Test AI integration
    ai_success = test_groq_integration()
    
    # Test template fallback
    template_success = test_template_fallback()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   AI Integration: {'✅ PASS' if ai_success else '❌ FAIL'}")
    print(f"   Template Fallback: {'✅ PASS' if template_success else '❌ FAIL'}")
    
    if ai_success:
        print("\n🎉 Congratulations! Your Groq API integration is working perfectly!")
        print("You can now generate AI-powered proposals through the application.")
    elif template_success:
        print("\n⚠️  AI integration failed, but template-based generation is working.")
        print("Check your API key and internet connection.")
    else:
        print("\n❌ Both AI and template generation failed.")
        print("Please check your setup and try again.")
    
    print("\n📚 For help, see: GROQ_SETUP_GUIDE.md") 