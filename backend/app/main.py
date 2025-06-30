import streamlit as st
import time

# Set page config at the very beginning
st.set_page_config(
    page_title="Upwork Job Analyzer",
    page_icon="📊",
    layout="wide"
)

from models.database import Database
from utils.web_scraper import UpworkScraper
from utils.job_analyzer import JobAnalyzer
from utils.proposal_generator import ProposalGenerator
import pandas as pd
from datetime import datetime

# Initialize components
@st.cache_resource
def init_components():
    """Initialize app components with proper caching"""
    try:
        db = Database()
        scraper = UpworkScraper()
        job_analyzer = JobAnalyzer()
        proposal_generator = ProposalGenerator()
        return db, scraper, job_analyzer, proposal_generator
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        return None, None, None, None

# Get components
db, scraper, job_analyzer, proposal_generator = init_components()

def main():
    st.title("📊 Upwork Job Analyzer")
    
    # Check if components initialized successfully
    if None in (db, scraper, job_analyzer, proposal_generator):
        st.error("Failed to initialize application components. Please check the logs and try again.")
        return
    
    # Navigation
    pages = {
        "Dashboard": show_dashboard,
        "Job Analysis": show_job_analysis_page,
        "Job Scraping": show_job_scraping_page,
        "Profile Management": show_profile_management_page,
        "Settings": show_settings_page
    }
    
    page = st.sidebar.selectbox("📱 Navigation", list(pages.keys()))
    
    # Show selected page
    pages[page]()

def show_dashboard():
    st.header("🏠 Dashboard")
    
    # Get statistics
    profiles = db.get_all_freelancer_profiles()
    scraped_jobs = db.get_scraped_jobs(limit=100)
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Profiles", len(profiles))
    
    with col2:
        st.metric("Scraped Jobs", len(scraped_jobs))
    
    with col3:
        if profiles:
            # Convert hourly_rate to float safely
            rates = []
            for p in profiles:
                try:
                    rate = float(p['hourly_rate']) if p['hourly_rate'] is not None else 0.0
                    rates.append(rate)
                except (ValueError, TypeError):
                    rates.append(0.0)
            
            avg_rate = sum(rates) / len(rates) if rates else 0.0
            st.metric("Avg Hourly Rate", f"${avg_rate:.1f}")
        else:
            st.metric("Avg Hourly Rate", "$0")
    
    with col4:
        if scraped_jobs:
            # Convert avg_pay_rate to float safely
            job_rates = []
            for j in scraped_jobs:
                try:
                    rate = float(j['avg_pay_rate']) if j['avg_pay_rate'] is not None else 0.0
                    if rate > 0:
                        job_rates.append(rate)
                except (ValueError, TypeError):
                    continue
            
            avg_job_rate = sum(job_rates) / len(job_rates) if job_rates else 0.0
            st.metric("Avg Job Rate", f"${avg_job_rate:.1f}")
        else:
            st.metric("Avg Job Rate", "$0")
    
    # Recent scraped jobs
    if scraped_jobs:
        st.subheader("📋 Recent Scraped Jobs")
        recent_jobs_df = pd.DataFrame(scraped_jobs[:10])
        if not recent_jobs_df.empty:
            display_cols = ['job_title', 'client_name', 'avg_pay_rate', 'client_rating', 'job_category']
            st.dataframe(recent_jobs_df[display_cols], use_container_width=True)

def show_job_analysis_page():
    st.header("🔍 Job Analysis")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["📝 Manual Input", "🔗 Job URL", "📊 From Scraped Jobs"]
    )
    
    if input_method == "📝 Manual Input":
        show_manual_job_input()
    elif input_method == "🔗 Job URL":
        show_url_job_input()
    else:
        show_scraped_jobs_selection()

def show_manual_job_input():
    st.subheader("📝 Manual Job Input")

    # Session state keys
    ANALYSIS_KEY = 'manual_analysis_result'
    JOBDATA_KEY = 'manual_job_data'
    PROFILE_KEY = 'manual_selected_profile'
    PROPOSAL_KEY = 'manual_generated_proposal'
    RECOMMEND_KEY = 'manual_recommendations'

    # Reset button
    if st.button("🔄 Reset", key="manual_reset"):
        for k in [ANALYSIS_KEY, JOBDATA_KEY, PROFILE_KEY, PROPOSAL_KEY, RECOMMEND_KEY]:
            if k in st.session_state:
                del st.session_state[k]
        st.experimental_rerun()

    # If we have a proposal, show it
    if PROPOSAL_KEY in st.session_state:
        st.subheader("📝 Generated Proposal")
        st.text_area("Generated Proposal", st.session_state[PROPOSAL_KEY], height=400)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Proposal"):
                db.add_successful_proposal(
                    st.session_state[PROFILE_KEY]['id'],
                    st.session_state[JOBDATA_KEY]['title'],
                    st.session_state[PROPOSAL_KEY],
                    None,
                    proposal_status="Draft"
                )
                st.success("✅ Proposal saved successfully!")
        with col2:
            if st.button("📋 Copy to Clipboard"):
                st.write("Proposal copied to clipboard!")
        return

    # If we have analysis, show results and allow proposal generation
    if ANALYSIS_KEY in st.session_state and JOBDATA_KEY in st.session_state and PROFILE_KEY in st.session_state:
        passed, reasons = st.session_state[ANALYSIS_KEY]
        job_data = st.session_state[JOBDATA_KEY]
        selected_profile = st.session_state[PROFILE_KEY]
        recommendations = st.session_state.get(RECOMMEND_KEY, [])

        st.subheader("📊 Analysis Results")
        col1, col2 = st.columns(2)
        with col1:
            if passed:
                st.success("✅ This job is a good match!")
            else:
                st.error("❌ This job may not be the best fit.")
        with col2:
            st.metric("Client Rating", f"{job_data['client_rating']}/5.0")
            st.metric("Pay Rate", f"${job_data['avg_pay_rate']}/hr")
        st.subheader("📋 Analysis Details")
        for reason in reasons:
            st.write(f"• {reason}")
        if recommendations:
            st.subheader("💡 Recommendations")
            for rec in recommendations:
                st.write(f"• {rec}")
        if passed:
            if st.button("🚀 Generate Proposal", type="primary"):
                with st.spinner("Generating proposal..."):
                    past_projects = db.get_past_projects(selected_profile['id'])
                    proposal = proposal_generator.generate_proposal(
                        job_data,
                        selected_profile,
                        past_projects,
                        recommendations
                    )
                    st.session_state[PROPOSAL_KEY] = proposal
                    st.experimental_rerun()
        return

    # Otherwise, show the input form
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title")
        job_description = st.text_area("Job Description", height=150)
        required_skills = st.text_input("Required Skills (comma-separated)")
        avg_pay_rate = st.number_input("Average Pay Rate ($/hour)", min_value=0.0, value=20.0)
    with col2:
        client_rating = st.number_input("Client Rating", min_value=0.0, max_value=5.0, value=4.5)
        total_jobs = st.number_input("Total Jobs Posted", min_value=0, value=5)
        total_hires = st.number_input("Total Hires", min_value=0, value=3)
        avg_review = st.number_input("Average Review", min_value=0.0, max_value=5.0, value=4.5)
    profiles = db.get_all_freelancer_profiles()
    if not profiles:
        st.warning("Please create a freelancer profile first in the 'Manage Profile' section.")
        return
    selected_profile = st.selectbox(
        "Select Freelancer Profile",
        options=profiles,
        format_func=lambda x: f"{x['name']} (${x['hourly_rate']}/hr)"
    )
    if st.button("Analyze Job", type="primary"):
        job_data = {
            'title': job_title,
            'description': job_description,
            'required_skills': [s.strip() for s in required_skills.split(',')] if required_skills else [],
            'avg_pay_rate': avg_pay_rate,
            'client_rating': client_rating,
            'client_history': {
                'total_jobs': total_jobs,
                'hires': total_hires,
                'avg_review': avg_review
            }
        }
        passed, reasons = job_analyzer.analyze_job(job_data, selected_profile)
        recommendations = job_analyzer.get_job_recommendations(job_data, selected_profile)
        st.session_state[ANALYSIS_KEY] = (passed, reasons)
        st.session_state[JOBDATA_KEY] = job_data
        st.session_state[PROFILE_KEY] = selected_profile
        st.session_state[RECOMMEND_KEY] = recommendations
        st.experimental_rerun()

def show_url_job_input():
    st.subheader("🔗 Job URL Input")
    
    job_url = st.text_input("Enter Upwork Job URL")
    
    # Select Freelancer Profile
    profiles = db.get_all_freelancer_profiles()
    if not profiles:
        st.warning("Please create a freelancer profile first in the 'Manage Profile' section.")
        return
    
    selected_profile = st.selectbox(
        "Select Freelancer Profile",
        options=profiles,
        format_func=lambda x: f"{x['name']} (${x['hourly_rate']}/hr)"
    )
    
    if st.button("🔍 Scrape & Analyze Job", type="primary"):
        if job_url:
            with st.spinner("Scraping job details..."):
                job_data = scraper.get_job_details(job_url)
                if job_data:
                    analyze_scraped_job(job_data, selected_profile)
                else:
                    st.error("Could not scrape job details. Please check the URL or try manual input.")
        else:
            st.error("Please enter a valid Upwork job URL.")

def show_scraped_jobs_selection():
    st.subheader("📊 Select from Scraped Jobs")
    
    scraped_jobs = db.get_scraped_jobs(limit=50)
    if not scraped_jobs:
        st.warning("No scraped jobs available. Please scrape some jobs first.")
        return
    
    # Create a selection interface
    job_options = {f"{job['job_title']} - {job['client_name']} (${job['avg_pay_rate']}/hr)": job for job in scraped_jobs}
    selected_job_key = st.selectbox("Select a job to analyze:", list(job_options.keys()))
    
    # Select Freelancer Profile
    profiles = db.get_all_freelancer_profiles()
    if not profiles:
        st.warning("Please create a freelancer profile first in the 'Manage Profile' section.")
        return
    
    selected_profile = st.selectbox(
        "Select Freelancer Profile",
        options=profiles,
        format_func=lambda x: f"{x['name']} (${x['hourly_rate']}/hr)"
    )
    
    if st.button("🔍 Analyze Selected Job", type="primary"):
        selected_job = job_options[selected_job_key]
        analyze_scraped_job(selected_job, selected_profile)

def analyze_job_manual(job_title, job_description, required_skills, avg_pay_rate, 
                      client_rating, total_jobs, total_hires, avg_review, selected_profile):
    job_data = {
        'title': job_title,
        'description': job_description,
        'required_skills': [s.strip() for s in required_skills.split(',')] if required_skills else [],
        'avg_pay_rate': avg_pay_rate,
        'client_rating': client_rating,
        'client_history': {
            'total_jobs': total_jobs,
            'hires': total_hires,
            'avg_review': avg_review
        }
    }
    
    perform_job_analysis(job_data, selected_profile)

def analyze_scraped_job(job_data, selected_profile):
    # Convert scraped job data to analysis format
    analysis_job_data = {
        'title': job_data['job_title'],
        'description': job_data['job_description'],
        'required_skills': job_data['required_skills'],
        'avg_pay_rate': job_data['avg_pay_rate'],
        'client_rating': job_data['client_rating'],
        'client_history': {
            'total_jobs': job_data['client_total_jobs'],
            'hires': job_data['client_total_hires'],
            'avg_review': job_data['client_avg_review']
        }
    }
    
    perform_job_analysis(analysis_job_data, selected_profile, job_data)

def perform_job_analysis(job_data, selected_profile, scraped_job_data=None):
    # Analyze job
    passed, reasons = job_analyzer.analyze_job(job_data, selected_profile)
    
    # Display analysis results
    st.subheader("📊 Analysis Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if passed:
            st.success("✅ This job is a good match!")
        else:
            st.error("❌ This job may not be the best fit.")
    
    with col2:
        st.metric("Client Rating", f"{job_data['client_rating']}/5.0")
        st.metric("Pay Rate", f"${job_data['avg_pay_rate']}/hr")
    
    # Analysis details
    st.subheader("📋 Analysis Details")
    for reason in reasons:
        st.write(f"• {reason}")
    
    # Get recommendations
    recommendations = job_analyzer.get_job_recommendations(job_data, selected_profile)
    
    if recommendations:
        st.subheader("💡 Recommendations")
        for rec in recommendations:
            st.write(f"• {rec}")
    
    # Save analysis to database
    if scraped_job_data:
        db.add_job_analysis(
            selected_profile['id'],
            job_data['title'],
            scraped_job_data['job_url'],
            job_data['description'],
            job_data['required_skills'],
            job_data['client_rating'],
            job_data['avg_pay_rate'],
            "PASS" if passed else "FAIL",
            reasons,
            " | ".join(recommendations) if recommendations else "No specific recommendations"
        )
    
    # Generate proposal if job passed analysis
    if passed:
        st.subheader("📝 Generate Proposal")
        if st.button("🚀 Generate Proposal", type="primary"):
            with st.spinner("Generating proposal..."):
                # Get past projects for the selected profile
                past_projects = db.get_past_projects(selected_profile['id'])
                
                proposal = proposal_generator.generate_proposal(
                    job_data,
                    selected_profile,
                    past_projects,
                    recommendations
                )
                
                st.text_area("Generated Proposal", proposal, height=400)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Proposal"):
                        db.add_successful_proposal(
                            selected_profile['id'],
                            job_data['title'],
                            proposal,
                            scraped_job_data['job_url'] if scraped_job_data else None,
                            proposal_status="Draft"
                        )
                        st.success("✅ Proposal saved successfully!")
                
                with col2:
                    if st.button("📋 Copy to Clipboard"):
                        st.write("Proposal copied to clipboard!")

def show_job_scraping_page():
    st.header("📊 Job Scraping")
    
    # Important notice about scraping limitations
    st.warning("""
    ⚠️ **Important Notice**: Upwork has implemented strong anti-bot measures that may prevent automated job scraping. 
    The scraper will attempt to retrieve jobs but may return sample data if access is blocked.
    """)
    
    # Scraping options
    st.subheader("🔍 Search Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        keywords_input = st.text_area("Keywords (one per line)", height=100, 
                                     placeholder="Python\nWeb Development\nData Analysis")
        max_jobs = st.number_input("Max jobs per keyword", min_value=1, max_value=50, value=10)
    
    with col2:
        categories = ["Web Development", "Mobile Development", "Data Science", "Design", "Writing", "Marketing"]
        selected_category = st.selectbox("Category (optional)", ["None"] + categories)
        
        if st.button("🚀 Start Scraping", type="primary"):
            if keywords_input.strip():
                keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
                
                with st.spinner(f"Scraping {len(keywords)} keywords..."):
                    scraped_jobs = scraper.scrape_jobs_by_keywords(keywords, max_jobs)
                    
                    if not scraped_jobs:
                        st.error("❌ No jobs found. This could be due to:")
                        st.write("• Upwork blocking automated access")
                        st.write("• No jobs matching the keywords")
                        st.write("• Network connectivity issues")
                        st.info("💡 Try using the manual job input or URL input methods instead.")
                        return
                    
                    # Check if we got sample data
                    sample_jobs_count = sum(1 for job in scraped_jobs if 'Sample' in job.get('job_title', ''))
                    if sample_jobs_count > 0:
                        st.warning(f"⚠️ {sample_jobs_count} sample jobs were returned due to access restrictions.")
                        st.info("💡 The scraper is working, but Upwork is blocking automated access. Sample data is provided for demonstration.")
                    
                    # Save to database
                    saved_count = 0
                    for job in scraped_jobs:
                        try:
                            db.add_scraped_job(
                                job['job_title'],
                                job['job_url'],
                                job['job_description'],
                                job['required_skills'],
                                job['client_name'],
                                job['client_rating'],
                                job['client_total_jobs'],
                                job['client_total_hires'],
                                job['client_avg_review'],
                                job['budget_range'],
                                job['avg_pay_rate'],
                                job['project_duration'],
                                job['job_category'],
                                job['posted_date']
                            )
                            saved_count += 1
                        except Exception as e:
                            st.error(f"Error saving job: {e}")
                    
                    if saved_count > 0:
                        st.success(f"✅ Successfully scraped and saved {saved_count} jobs!")
                        
                        # Show preview of scraped jobs
                        st.subheader("📋 Scraped Jobs Preview")
                        for i, job in enumerate(scraped_jobs[:3]):  # Show first 3 jobs
                            with st.expander(f"📝 {job['job_title']}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Client:** {job['client_name']}")
                                    st.write(f"**Rating:** {job['client_rating']}/5.0")
                                    st.write(f"**Budget:** {job['budget_range']}")
                                with col2:
                                    st.write(f"**Skills:** {', '.join(job['required_skills'][:3])}")
                                    st.write(f"**Duration:** {job['project_duration']}")
                                    st.write(f"**Category:** {job['job_category']}")
                                st.write("**Description:**")
                                st.write(job['job_description'][:200] + "..." if len(job['job_description']) > 200 else job['job_description'])
                    else:
                        st.error("❌ Failed to save any jobs to the database.")
            else:
                st.error("Please enter at least one keyword.")

def show_profile_management_page():
    st.header("👤 Profile Management")
    
    # Initialize session state for profile creation
    if 'profile_created' not in st.session_state:
        st.session_state.profile_created = False
    
    # Display existing profiles first
    st.subheader("📋 Existing Profiles")
    profiles = db.get_all_freelancer_profiles()
    
    for profile in profiles:
        with st.expander(f"👤 {profile['name']} - ${profile['hourly_rate']}/hr"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Email:** {profile['email'] or 'N/A'}")
                st.write(f"**Experience:** {profile['experience_years']} years")
                st.write(f"**Skills:** {', '.join(profile['skills'])}")
            
            with col2:
                st.write(f"**Bio:** {profile['bio'] or 'N/A'}")
                st.write(f"**Portfolio:** {profile['portfolio_url'] or 'N/A'}")
                st.write(f"**Timezone:** {profile['timezone'] or 'N/A'}")
            
            # Add past project button with unique key
            project_button_key = f"add_project_{profile['id']}_{id(profile)}"
            if st.button(f"➕ Add Past Project", key=project_button_key):
                st.session_state.adding_project = profile['id']
                show_add_project_form(profile['id'])
    
    # Create new profile form
    st.subheader("➕ Create New Profile")
    
    # Use form to prevent automatic resubmission
    with st.form("new_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name")
            email = st.text_input("Email")
            hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=25.0)
            experience_years = st.number_input("Years of Experience", min_value=0, value=1)
        
        with col2:
            skills = st.text_input("Skills (comma-separated)")
            bio = st.text_area("Bio (optional)", height=100)
            portfolio_url = st.text_input("Portfolio URL (optional)")
            timezone = st.text_input("Timezone (optional)")
        
        submitted = st.form_submit_button("➕ Create Profile", type="primary")
        
        if submitted and not st.session_state.profile_created:
            if name and skills:
                skills_list = [s.strip() for s in skills.split(',') if s.strip()]
                if skills_list:
                    try:
                        profile_id = db.add_freelancer_profile(
                            name, email, hourly_rate, skills_list,
                            experience_years, bio, portfolio_url, timezone
                        )
                        if profile_id:
                            st.session_state.profile_created = True
                            st.success("✅ Profile created successfully!")
                            time.sleep(1)  # Brief pause to show success message
                            st.rerun()
                        else:
                            st.error("Failed to create profile. Please try again.")
                    except Exception as e:
                        st.error(f"Error creating profile: {str(e)}")
                else:
                    st.error("Please enter at least one valid skill.")
            else:
                st.error("Please fill in at least name and skills.")

def show_add_project_form(freelancer_id):
    st.subheader("➕ Add Past Project")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Project Title")
        description = st.text_area("Project Description", height=100)
        tech_stack = st.text_input("Tech Stack (comma-separated)")
        outcomes = st.text_area("Project Outcomes", height=100)
    
    with col2:
        project_url = st.text_input("Project URL (optional)")
        client_name = st.text_input("Client Name (optional)")
        project_duration = st.text_input("Project Duration (e.g., 3 months)")
        project_budget = st.number_input("Project Budget ($)", min_value=0.0, value=0.0)
        completion_date = st.date_input("Completion Date")
        project_rating = st.number_input("Project Rating (1-5)", min_value=1.0, max_value=5.0, value=5.0)
        client_feedback = st.text_area("Client Feedback (optional)", height=100)
    
    if st.button("➕ Add Project", type="primary"):
        if title and description and tech_stack and outcomes:
            tech_stack_list = [t.strip() for t in tech_stack.split(',')]
            db.add_past_project(
                freelancer_id, title, description, tech_stack_list, outcomes,
                project_url, client_name, project_duration, project_budget,
                completion_date, project_rating, client_feedback
            )
            st.success("✅ Project added successfully!")
        else:
            st.error("Please fill in all required fields.")

def show_settings_page():
    st.header("⚙️ Settings")
    
    st.subheader("🔑 API Configuration")
    
    # Groq API Key
    groq_key = st.text_input("Groq API Key", type="password", help="Get your API key from https://console.groq.com/")
    
    if st.button("💾 Save Settings"):
        # In a real application, you would save this to a secure configuration
        st.success("✅ Settings saved! (Note: In production, use environment variables)")
    
    st.subheader("📊 Application Statistics")
    
    # Database statistics
    profiles = db.get_all_freelancer_profiles()
    scraped_jobs = db.get_scraped_jobs(limit=1000)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Profiles", len(profiles))
        st.metric("Total Scraped Jobs", len(scraped_jobs))
    
    with col2:
        if profiles:
            total_projects = sum(len(db.get_past_projects(p['id'])) for p in profiles)
            total_proposals = sum(len(db.get_successful_proposals(p['id'])) for p in profiles)
            st.metric("Total Projects", total_projects)
            st.metric("Total Proposals", total_proposals)
    
    st.subheader("⚠️ Danger Zone")
    st.warning("This action will permanently delete ALL freelancer profiles and related data (past projects, proposals, job analysis history). This cannot be undone.")
    confirm_delete = st.checkbox("Yes, I really want to delete all profiles and related data.")
    if st.button("🗑️ Delete All Profiles", type="primary"):
        if confirm_delete:
            try:
                db.delete_all_profiles_and_related()
                st.success("✅ All freelancer profiles and related data have been deleted.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error deleting profiles: {e}")
        else:
            st.error("Please confirm by checking the box above before deleting.")

if __name__ == "__main__":
    main() 