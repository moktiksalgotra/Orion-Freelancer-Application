import os
import re
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
try:
    load_dotenv()
except Exception as e:
    print(f"⚠️ Warning: Could not load .env file: {e}")
    print("Continuing without .env file...")

class ProposalGenerator:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                import groq
                self.client = groq.Groq(api_key=api_key)
                self.model = "llama-3.3-70b-versatile"
                self.use_ai = True
                print("✅ AI-powered proposal generation enabled with LLaMA 3.3")
            except ImportError:
                print("⚠️ Warning: Groq library not installed. Run: pip install groq")
                print("Using template-based proposal generation instead.")
                self.use_ai = False
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize Groq client: {e}")
                print("Using template-based proposal generation instead.")
                self.use_ai = False
        else:
            print("ℹ️ Note: Using template-based proposal generation. Set GROQ_API_KEY for AI-powered proposals.")
            self.use_ai = False

    def generate_proposal(
        self,
        job_title: str,
        job_description: str,
        required_skills: List[str],
        freelancer_name: str,
        freelancer_skills: List[str],
        freelancer_experience: int,
        freelancer_bio: str = None,
        github_url: str = None,
        linkedin_url: str = None,
        relevant_experience: List[Dict] = None,
        past_projects: List[Dict] = None,
        successful_proposals: List[Dict] = None,
        use_ai: bool = True
    ) -> str:
        """
        Generate a proposal using AI or template-based generation.
        """
        # Prepare job data for the generator
        job_data = {
            'title': job_title,
            'description': job_description,
            'required_skills': required_skills
        }
        
        # Prepare freelancer profile
        freelancer_profile = {
            'name': freelancer_name,
            'skills': freelancer_skills,
            'experience_years': freelancer_experience,
            'bio': freelancer_bio or "",
            'github_url': github_url or "",
            'linkedin_url': linkedin_url or "",
            'relevant_experience': relevant_experience or []
        }
        
        # Prepare recommendations (empty for now, could be enhanced)
        recommendations = []
        
        if use_ai and self.use_ai:
            return self._generate_ai_proposal(job_data, freelancer_profile, past_projects or [], recommendations)
        else:
            return self._generate_template_proposal(job_data, freelancer_profile, past_projects or [], recommendations)

    def _generate_ai_proposal(
        self,
        job_data: Dict,
        freelancer_profile: Dict,
        past_projects: List[Dict],
        recommendations: List[str]
    ) -> str:
        """
        Generate a proposal using LLaMA 3.3 via Groq.
        """
        try:
            # Construct the prompt
            prompt = self._construct_ai_prompt(job_data, freelancer_profile, past_projects, recommendations)
            
            # Generate the proposal using LLaMA 3.3
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert freelancer proposal writer with deep knowledge of various industries and technologies. Your task is to write compelling, personalized proposals that:

1. Address the client's specific needs and requirements directly
2. Highlight relevant experience and skills that match the job requirements
3. Demonstrate understanding of the project scope and challenges
4. Show value proposition and unique selling points
5. Include specific, actionable questions that show engagement
6. Maintain a professional yet approachable tone
7. Structure the proposal clearly with proper sections
8. Keep the proposal concise but comprehensive (800-1200 words)

Format the proposal with clear sections: Executive Summary, Relevant Experience, Key Qualifications, Project Approach, Questions for Client, and Professional Closing."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ AI generation failed: {e}")
            print("Falling back to template-based generation...")
            return self._generate_template_proposal(job_data, freelancer_profile, past_projects, recommendations)

    def _construct_ai_prompt(
        self,
        job_data: Dict,
        freelancer_profile: Dict,
        past_projects: List[Dict],
        recommendations: List[str]
    ) -> str:
        """
        Construct a detailed prompt for AI proposal generation.
        """
        # Format past projects for context
        projects_context = ""
        if past_projects:
            projects_context = "\n\nRelevant Past Projects:\n"
            for i, project in enumerate(past_projects[:3], 1):  # Top 3 most relevant
                projects_context += f"{i}. {project.get('title', 'Project')}: {project.get('description', '')}\n"
                if project.get('technologies'):
                    projects_context += f"   Technologies: {', '.join(project['technologies'])}\n"
                projects_context += f"   Duration: {project.get('duration', 'N/A')}\n\n"

        # Format relevant experience
        experience_context = ""
        if freelancer_profile['relevant_experience']:
            experience_context = "\n\nRelevant Experience:\n"
            for exp in freelancer_profile['relevant_experience'][:3]:  # Top 3 most relevant
                experience_context += f"• {exp.get('title', 'Role')}: {exp.get('description', '')}\n"
                if exp.get('technologies'):
                    experience_context += f"  Technologies: {', '.join(exp['technologies'])}\n"

        prompt = f"""Please write a compelling freelance proposal for the following job:

JOB DETAILS:
Title: {job_data['title']}
Description: {job_data['description']}
Required Skills: {', '.join(job_data['required_skills'])}

FREELANCER PROFILE:
Name: {freelancer_profile['name']}
Skills: {', '.join(freelancer_profile['skills'])}
Years of Experience: {freelancer_profile['experience_years']}
Bio: {freelancer_profile['bio']}
GitHub: {freelancer_profile['github_url']}
LinkedIn: {freelancer_profile['linkedin_url']}{experience_context}{projects_context}

INSTRUCTIONS:
1. Write a personalized proposal that directly addresses the job requirements
2. Highlight specific skills and experience that match the required skills
3. Include relevant past projects and achievements
4. Ask thoughtful questions about the project scope, timeline, and requirements
5. Demonstrate understanding of the client's needs
6. Show enthusiasm and confidence in delivering the project
7. Keep the tone professional but approachable
8. Structure the proposal with clear sections
9. Include a call to action for next steps

Please generate a complete, ready-to-send proposal that would help win this job."""

        return prompt

    def _generate_template_proposal(
        self,
        job_data: Dict,
        freelancer_profile: Dict,
        past_projects: List[Dict],
        recommendations: List[str]
    ) -> str:
        """
        Generate a professional proposal using a plain-text, client-ready format.
        """
        relevant_projects = self._format_relevant_projects(past_projects, job_data['required_skills'])
        relevant_experience = self._format_relevant_experience(freelancer_profile['relevant_experience'])
        
        def linkify(text):
            if not text:
                return ""
            url_pattern = re.compile(r'(https?://\S+)')
            return url_pattern.sub(r'\1', text)

        # Executive Summary
        executive_summary = f"""
Hello {job_data['title']}, I appreciate the opportunity to apply for the {job_data['title']} position. With my expertise in {', '.join(job_data['required_skills'])}, I am confident in delivering a high-quality solution that meets your requirements.
"""

        # Relevant Experience
        relevant_experience_section = f"""
Relevant Experience:

{relevant_experience if relevant_experience else f'I have successfully completed numerous projects that demonstrate my expertise in {", ".join(job_data["required_skills"])} and related technologies.'}
"""

        # Key Qualifications
        key_qualifications = f"""
✅ Why I am a Fit:

✅ {', '.join(job_data['required_skills'])} Expertise – {freelancer_profile['experience_years']} years of hands-on experience developing and deploying production-ready applications
✅ {', '.join(freelancer_profile['skills'][:2])} Proficiency – Deep understanding of modern development practices and best practices
✅ Problem-Solving Skills – Proven ability to analyze complex requirements and deliver scalable solutions
✅ Communication & Collaboration – Experience working with cross-functional teams and stakeholders
✅ Quality Assurance – Strong focus on testing, documentation, and maintaining code quality
"""

        # Questions for Client
        questions_section = f"""
✅ Questions About the Project:

1. What are the key features and functionalities you want in the {job_data['title'].lower()} solution?
2. Who is your target audience, and what are their specific needs and expectations?
3. What is your preferred technology stack, and are there any specific tools or frameworks you would like me to use?
4. What is your timeline for this project, and are there any specific milestones or deadlines I should be aware of?
5. What is your budget for this project, and what key performance indicators (KPIs) will you use to measure success?
"""

        # Professional Links
        professional_links = ""
        if freelancer_profile['github_url'] or freelancer_profile['linkedin_url']:
            links = []
            if freelancer_profile['github_url']:
                links.append(f"GitHub: {linkify(freelancer_profile['github_url'])}")
            if freelancer_profile['linkedin_url']:
                links.append(f"LinkedIn: {linkify(freelancer_profile['linkedin_url'])}")
            links_text = '\n'.join(links) if links else ''
            professional_links = f"""
Professional Links:

{links_text}
"""
        else:
            professional_links = """
Professional Links:

(GitHub, LinkedIn, Portfolio: Available upon request)
"""

        # Conclusion
        closing = f"""
I am excited about the possibility of bringing my {', '.join(job_data['required_skills'][:2])} expertise and real-world application experience to this project. Looking forward to discussing further!

Best regards,
{freelancer_profile['name']}
"""

        # Combine all sections
        proposal = f"""{executive_summary}\n{relevant_experience_section}\n{key_qualifications}\n{questions_section}\n{professional_links}\n{closing}"""

        return proposal.strip()

    def _format_relevant_experience(self, relevant_experience: List[Dict]) -> str:
        """Format relevant experience projects for proposal inclusion with professional link formatting"""
        if not relevant_experience:
            return ""
        
        formatted_experience = []
        
        for i, project in enumerate(relevant_experience, 1):
            if isinstance(project, dict):
                # Handle structured project data
                title = project.get('project_title', project.get('title', ''))
                description = project.get('project_description', project.get('description', ''))
                url = project.get('project_url', project.get('url', ''))
                company = project.get('company_name', project.get('company', ''))
                technologies = project.get('technologies_used', [])
                achievements = project.get('key_achievements', '')
                duration = project.get('project_duration', '')
                
                # Format the project entry
                project_entry = f"{i}. "
                
                if url:
                    project_entry += f"{title} ([View Project]({url}))"
                else:
                    project_entry += f"{title}"
                
                if company:
                    project_entry += f", {company}"
                
                project_entry += f": {description}"
                
                # Add technologies if available
                if technologies and isinstance(technologies, list):
                    tech_list = ', '.join(technologies[:5])  # Limit to 5 technologies
                    project_entry += f" Technologies: {tech_list}."
                
                # Add achievements if available
                if achievements:
                    project_entry += f" Key achievements: {achievements}"
                
                # Add duration if available
                if duration:
                    project_entry += f" Duration: {duration}."
                
                formatted_experience.append(project_entry)
            elif isinstance(project, str):
                # Handle simple string entries
                formatted_experience.append(f"{i}. {project}")
        
        return "\n\n".join(formatted_experience)

    def _format_relevant_projects(self, past_projects: List[Dict], required_skills: List[str]) -> str:
        """
        Format and filter relevant past projects based on required skills.
        """
        required_skills = set(skill.lower() for skill in required_skills)
        relevant_projects = []
        
        for project in past_projects:
            project_skills = set(skill.lower() for skill in project.get('tech_stack', []))
            if project_skills & required_skills:  # If there's any overlap in skills
                relevant_projects.append(
                    f"✅ {project.get('title', 'Project')}\n"
                    f"  Technologies: {', '.join(project.get('tech_stack', []))}\n"
                    f"  Outcome: {project.get('outcomes', 'N/A')}\n"
                )
        
        if not relevant_projects:
            return "✅ No directly relevant past projects available."
        
        return "\n".join(relevant_projects)

    def _generate_job_questions(self, job_data: Dict) -> str:
        """
        Generate job-related questions for the template-based proposal.
        """
        questions = [
            f"✅ Are there any specific {job_data['title'].lower()} requirements or constraints?",
            f"✅ What is the expected timeline for this {job_data['title'].lower()} project?",
            f"✅ Are there any specific technologies or platforms that must be used?",
            f"✅ What is the budget range for this {job_data['title'].lower()} project?",
            f"✅ Are there any regulatory or compliance requirements that must be prioritized?"
        ]
        return "\n".join(questions)

    def _generate_contribution_points(self, job_data: Dict, freelancer_profile: Dict) -> str:
        """
        Generate contribution points for the template-based proposal.
        """
        points = [
            f"✅ {job_data['title']} Development – Implementing robust solutions with {', '.join(freelancer_profile['skills'][:2])} expertise.",
            f"✅ {', '.join(freelancer_profile['skills'][:2])} Integration – Ensuring seamless interoperability and optimal performance.",
            f"✅ Quality Assurance & Testing – Comprehensive testing and validation to ensure reliability.",
            f"✅ Documentation & Support – Providing detailed documentation and ongoing support."
        ]
        return "\n".join(points) 