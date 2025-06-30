import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

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
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize Groq client: {e}")
                print("Using template-based proposal generation instead.")
                self.use_ai = False
        else:
            print("ℹ️ Note: Using template-based proposal generation. Set GROQ_API_KEY for AI-powered proposals.")
            self.use_ai = False

    def generate_proposal(
        self,
        job_data: Dict,
        freelancer_profile: Dict,
        past_projects: List[Dict],
        recommendations: List[str]
    ) -> str:
        """
        Generate a proposal using AI or template-based generation.
        """
        if self.use_ai:
            return self._generate_ai_proposal(job_data, freelancer_profile, past_projects, recommendations)
        else:
            return self._generate_template_proposal(job_data, freelancer_profile, past_projects, recommendations)

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
            prompt = self._construct_prompt(job_data, freelancer_profile, past_projects, recommendations)
            
            # Generate the proposal using LLaMA 3.3
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert freelancer proposal writer. Write compelling, personalized proposals that highlight relevant experience and address client needs directly. Focus on being professional, specific, and showing value."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ AI generation failed: {e}")
            print("Falling back to template-based generation...")
            return self._generate_template_proposal(job_data, freelancer_profile, past_projects, recommendations)

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
        
        # Executive Summary
        executive_summary = f"""
Hello {job_data.get('client_name', 'there')}, I appreciate the opportunity to apply for the {job_data['title']} position. With my expertise in {', '.join(job_data['required_skills'])}, I am confident in delivering a high-quality solution that meets your requirements.
"""

        # Relevant Experience
        relevant_experience_section = f"""
Relevant Experience:

{relevant_projects}
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

        # Value Proposition
        value_proposition = f"""
Value Proposition:
I bring a unique value proposition to this project, combining my technical expertise with a deep understanding of client needs. My experience in developing innovative solutions using {', '.join(freelancer_profile['skills'][:3])} enables me to provide cutting-edge solutions that meet your requirements. Additionally, my proficiency in {', '.join(job_data['required_skills'][:2])} ensures that I can deliver high-quality, responsive, and scalable applications. My goal is to provide tailored solutions that exceed expectations, while ensuring seamless execution and timely delivery.
"""

        # Proposed Approach
        proposed_approach = f"""
Proposed Approach:
My approach to this project will involve the following steps:
• Initial consultation to understand your requirements and goals
• Development of a tailored solution using {', '.join(job_data['required_skills'])}, with a focus on quality, scalability, and responsiveness
• Regular updates and progress reports to ensure you are informed and satisfied
• Testing and quality assurance to ensure the solution meets your expectations
• Deployment and maintenance of the solution, with ongoing support and updates as needed
"""

        # Professional Links
        professional_links = f"""
Professional Links:
For more information about my experience and skills, please visit my LinkedIn profile: [LinkedIn]({freelancer_profile.get('linkedin_url', 'https://linkedin.com/in/yourprofile')})
GitHub Profile: [GitHub]({freelancer_profile.get('github_url', 'https://github.com/yourusername')})
Portfolio: [Portfolio]({freelancer_profile.get('portfolio_url', 'https://yourportfolio.com')})
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

        # Conclusion
        closing = f"""
I am excited about the possibility of bringing my {', '.join(job_data['required_skills'][:2])} expertise and real-world application experience to this project. Looking forward to discussing further!

Best regards,
{freelancer_profile['name']}
"""

        # Combine all sections
        proposal = f"""{executive_summary}\n{relevant_experience_section}\n{key_qualifications}\n{value_proposition}\n{proposed_approach}\n{professional_links}\n{questions_section}\n{closing}"""

        return proposal.strip()

    def _construct_prompt(
        self,
        job_data: Dict,
        freelancer_profile: Dict,
        past_projects: List[Dict],
        recommendations: List[str]
    ) -> str:
        """
        Construct a detailed prompt for the AI model.
        """
        # Format past projects
        relevant_projects = self._format_relevant_projects(past_projects, job_data['required_skills'])
        
        prompt = f"""
Write a professional Upwork proposal for the following job:

Job Title: {job_data['title']}
Job Description: {job_data['description']}
Required Skills: {', '.join(job_data['required_skills'])}
Budget: ${job_data['avg_pay_rate']}/hour

Freelancer Profile:
- Name: {freelancer_profile['name']}
- Experience: {freelancer_profile['experience_years']} years
- Skills: {', '.join(freelancer_profile['skills'])}
- Hourly Rate: ${freelancer_profile['hourly_rate']}/hour
- LinkedIn: {freelancer_profile.get('linkedin_url', 'N/A')}
- GitHub: {freelancer_profile.get('github_url', 'N/A')}
- Portfolio: {freelancer_profile.get('portfolio_url', 'N/A')}

Relevant Past Projects:
{relevant_projects}

Special Recommendations to Address:
{chr(10).join('- ' + rec for rec in recommendations)}

Requirements for the proposal:
1. Start with a strong, personalized introduction addressing the client by name if available
2. Include a clear "Relevant Experience" section with numbered projects and links
3. Add a "Value Proposition" section highlighting unique benefits
4. Include a "Proposed Approach" section with bullet points
5. Add a "Professional Links" section with LinkedIn, GitHub, and Portfolio links
6. Address the client's specific needs mentioned in the job description
7. Highlight relevant past projects and experience with proper formatting
8. Address any skill gaps mentioned in recommendations
9. Include specific examples of how you would approach this project
10. End with a clear call to action
11. Keep it professional but conversational
12. Show enthusiasm for the project
13. Use plain text section headers WITHOUT any markdown formatting symbols like ## or **
14. Use checkmarks (✅) for key points instead of bold formatting
15. Use bullet points (•) for lists in the proposed approach
16. Format project links as [Project Name](URL) format
17. Include demo links and video links where available
18. Make the proposal comprehensive but concise (around 800-1200 words)

Please write a compelling proposal that demonstrates understanding of the project and highlights relevant experience with proper formatting and structure.
"""
        return prompt

    def _format_relevant_projects(self, past_projects: List[Dict], required_skills: List[str]) -> str:
        """
        Format and filter relevant past projects based on required skills.
        """
        required_skills = set(skill.lower() for skill in required_skills)
        relevant_projects = []
        
        for i, project in enumerate(past_projects, 1):
            project_skills = set(skill.lower() for skill in project['tech_stack'])
            if project_skills & required_skills:  # If there's any overlap in skills
                project_link = project.get('project_url', '')
                demo_link = project.get('demo_url', '')
                video_link = project.get('video_url', '')
                
                project_text = f"{i}. {project['title']}"
                if project_link:
                    project_text += f" ([View Project]({project_link}))"
                
                project_text += f"\n   Technologies: {', '.join(project['tech_stack'])}"
                project_text += f"\n   Outcome: {project['outcomes']}"
                
                if demo_link:
                    project_text += f"\n   Live Demo: [Demo]({demo_link})"
                
                if video_link:
                    project_text += f"\n   Demo Video: [Watch Demo]({video_link})"
                
                relevant_projects.append(project_text)
        
        if not relevant_projects:
            return f"✅ No directly relevant past projects available, but I have successfully completed numerous projects that demonstrate my expertise in {', '.join(required_skills)} and related technologies."
        
        return "\n\n".join(relevant_projects) 