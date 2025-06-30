#!/usr/bin/env python3
"""
Interactive CLI for testing Groq API integration
Run this script to test proposal generation interactively.
"""

import os
import sys
from dotenv import load_dotenv
from utils.proposal_generator import ProposalGenerator

def get_user_input(prompt, default=""):
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def interactive_test():
    """Interactive test of proposal generation"""
    print("🚀 Orion Freelancer Application - Interactive Groq Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("❌ GROQ_API_KEY not set. Please set it first:")
        print("1. Copy backend/env.example to backend/.env")
        print("2. Edit .env and add your API key")
        return
    
    # Initialize generator
    try:
        generator = ProposalGenerator()
        if not generator.use_ai:
            print("❌ AI is not enabled. Check your API key and try again.")
            return
        print("✅ Groq API initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    print("\n📝 Let's generate a test proposal!")
    print("(Press Enter to use default values)")
    
    # Get job details
    job_title = get_user_input("Job Title", "Full-Stack Web Developer")
    job_description = get_user_input(
        "Job Description", 
        "We need a skilled developer to build a modern web application with React frontend and Node.js backend."
    )
    required_skills = get_user_input("Required Skills (comma-separated)", "React, Node.js, MongoDB").split(",")
    required_skills = [skill.strip() for skill in required_skills]
    
    # Get freelancer details
    freelancer_name = get_user_input("Your Name", "John Doe")
    freelancer_skills = get_user_input("Your Skills (comma-separated)", "React, Node.js, MongoDB, JavaScript").split(",")
    freelancer_skills = [skill.strip() for skill in freelancer_skills]
    freelancer_experience = int(get_user_input("Years of Experience", "5"))
    freelancer_bio = get_user_input("Your Bio", "Experienced full-stack developer with expertise in modern web technologies.")
    github_url = get_user_input("GitHub URL", "https://github.com/johndoe")
    linkedin_url = get_user_input("LinkedIn URL", "https://linkedin.com/in/johndoe")
    
    # Choose generation method
    use_ai = get_user_input("Use AI generation? (y/n)", "y").lower() == "y"
    
    print(f"\n🎯 Generating {'AI-powered' if use_ai else 'template-based'} proposal...")
    print("=" * 60)
    
    try:
        proposal = generator.generate_proposal(
            job_title=job_title,
            job_description=job_description,
            required_skills=required_skills,
            freelancer_name=freelancer_name,
            freelancer_skills=freelancer_skills,
            freelancer_experience=freelancer_experience,
            freelancer_bio=freelancer_bio,
            github_url=github_url,
            linkedin_url=linkedin_url,
            use_ai=use_ai
        )
        
        print("✅ Proposal generated successfully!")
        print(f"📏 Length: {len(proposal)} characters")
        print("\n📄 Generated Proposal:")
        print("=" * 60)
        print(proposal)
        print("=" * 60)
        
        # Save option
        save = get_user_input("\nSave proposal to file? (y/n)", "n").lower() == "y"
        if save:
            filename = get_user_input("Filename", "generated_proposal.txt")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(proposal)
            print(f"✅ Proposal saved to {filename}")
        
    except Exception as e:
        print(f"❌ Failed to generate proposal: {e}")

def quick_test():
    """Quick test with default values"""
    print("⚡ Quick Test Mode")
    print("=" * 30)
    
    load_dotenv()
    
    try:
        generator = ProposalGenerator()
        if not generator.use_ai:
            print("❌ AI not enabled")
            return
        
        proposal = generator.generate_proposal(
            job_title="Python Data Analyst",
            job_description="Looking for a Python developer to analyze customer data and create visualizations.",
            required_skills=["Python", "Pandas", "Matplotlib"],
            freelancer_name="Data Expert",
            freelancer_skills=["Python", "Pandas", "NumPy", "Matplotlib", "Seaborn"],
            freelancer_experience=3,
            freelancer_bio="Data scientist with expertise in Python and statistical analysis.",
            use_ai=True
        )
        
        print("✅ Quick test successful!")
        print(f"📏 Proposal length: {len(proposal)} characters")
        print("\n📄 Sample:")
        print("-" * 40)
        print(proposal[:300] + "...")
        print("-" * 40)
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        interactive_test() 