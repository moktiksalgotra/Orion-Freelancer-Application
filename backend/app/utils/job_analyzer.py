import spacy
from typing import Dict, List, Tuple
import numpy as np

class JobAnalyzer:
    def __init__(self):
        try:
            # Try to load the large model with word vectors
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            print("Large language model not found. Please install it using:")
            print("python -m spacy download en_core_web_lg")
            # Fallback to small model if large is not available
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("Warning: Using small model. Skill matching will be less accurate.")
            except OSError:
                raise Exception("No spaCy model found. Please install a model using: python -m spacy download en_core_web_lg")
        
        self.min_hourly_rate = 15
        self.min_client_rating = 4.0

    def analyze_job(self, job_data: Dict, freelancer_profile: Dict) -> Tuple[bool, List[str]]:
        """
        Analyzes a job posting against given criteria and freelancer profile.
        Returns a tuple of (passed_analysis: bool, reasons: List[str])
        """
        reasons = []
        passed = True

        # Check client rating
        if job_data['client_rating'] < self.min_client_rating:
            reasons.append(f"Client rating ({job_data['client_rating']}) is below minimum threshold of {self.min_client_rating}")
            passed = False

        # Check hourly rate
        if job_data['avg_pay_rate'] < self.min_hourly_rate:
            reasons.append(f"Average pay rate (${job_data['avg_pay_rate']}/hr) is below minimum threshold of ${self.min_hourly_rate}/hr")
            passed = False

        # Check skill match
        skill_match_score, matched_skills = self._calculate_skill_match(
            job_data['required_skills'],
            freelancer_profile['skills']
        )

        if skill_match_score < 0.5:  # Requiring at least 50% skill match
            reasons.append(f"Skill match is too low ({skill_match_score:.0%})")
            passed = False
        else:
            reasons.append(f"Skills matched: {', '.join(matched_skills)}")

        # Client history analysis
        if self._analyze_client_history(job_data['client_history']):
            reasons.append("Client has positive hiring history")
        else:
            reasons.append("Client history raises concerns")
            passed = False

        return passed, reasons

    def _calculate_skill_match(self, required_skills: List[str], freelancer_skills: List[str]) -> Tuple[float, List[str]]:
        """
        Calculate the skill match score between required job skills and freelancer skills.
        Returns a tuple of (match_score: float, matched_skills: List[str])
        """
        if not required_skills:
            return 0.0, []
        required_skills = [skill.lower() for skill in required_skills]
        freelancer_skills = [skill.lower() for skill in freelancer_skills]
        
        matched_skills = []
        for req_skill in required_skills:
            # Check for exact matches
            if req_skill in freelancer_skills:
                matched_skills.append(req_skill)
                continue
            
            # Check for semantic similarity
            req_doc = self.nlp(req_skill)
            best_match_score = 0
            best_match = None
            
            for free_skill in freelancer_skills:
                free_doc = self.nlp(free_skill)
                similarity = req_doc.similarity(free_doc)
                
                if similarity > 0.8 and similarity > best_match_score:  # High similarity threshold
                    best_match_score = similarity
                    best_match = free_skill
            
            if best_match:
                matched_skills.append(best_match)

        match_score = len(matched_skills) / len(required_skills)
        return match_score, matched_skills

    def _analyze_client_history(self, client_history: Dict) -> bool:
        """
        Analyze client history to determine if it's favorable.
        Returns True if client history is good, False otherwise.
        """
        # Example criteria - can be adjusted based on requirements
        min_jobs_posted = 3
        min_avg_review = 4.0
        min_hire_rate = 0.5

        if client_history['total_jobs'] < min_jobs_posted:
            return False

        if client_history['avg_review'] < min_avg_review:
            return False

        hire_rate = client_history['hires'] / client_history['total_jobs']
        if hire_rate < min_hire_rate:
            return False

        return True

    def get_job_recommendations(self, job_data: Dict, freelancer_profile: Dict) -> List[str]:
        """
        Generate recommendations for approaching the job based on analysis.
        """
        recommendations = []
        
        # Analyze budget fit
        if job_data['avg_pay_rate'] < freelancer_profile['hourly_rate']:
            recommendations.append(
                "Consider negotiating the rate - the posted rate is below your usual rate"
            )

        # Skill-based recommendations
        required_skills = set(s.lower() for s in job_data['required_skills'])
        freelancer_skills = set(s.lower() for s in freelancer_profile['skills'])
        
        missing_skills = required_skills - freelancer_skills
        if missing_skills:
            recommendations.append(
                f"Address these required skills in your proposal: {', '.join(missing_skills)}"
            )

        # Project size recommendations
        if job_data.get('estimated_duration', '').lower().startswith('long term'):
            recommendations.append(
                "Emphasize your long-term availability and commitment in the proposal"
            )

        return recommendations 