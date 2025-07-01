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

    def analyze_job_fit(self, job_title: str, job_description: str, required_skills: List[str], 
                       client_rating: float, avg_pay_rate: float, freelancer_skills: List[str], 
                       freelancer_hourly_rate: float, freelancer_experience: int) -> Dict:
        """
        Analyze job fit based on the specified criteria.
        Returns a dictionary with analysis result, reasons, recommendation, and match level.
        """
        reasons = []
        passed = True
        recommendation = ""
        match_level = "LOW"  # Default match level

        # Check client rating
        if client_rating and client_rating < self.min_client_rating:
            reasons.append(f"Client rating ({client_rating}) is below minimum threshold of {self.min_client_rating}")
            passed = False
        elif client_rating:
            reasons.append(f"Client rating ({client_rating}) meets minimum threshold")

        # Check hourly rate
        if avg_pay_rate and avg_pay_rate < self.min_hourly_rate:
            reasons.append(f"Average pay rate (${avg_pay_rate}/hr) is below minimum threshold of ${self.min_hourly_rate}/hr")
            passed = False
        elif avg_pay_rate:
            reasons.append(f"Pay rate (${avg_pay_rate}/hr) meets minimum threshold")

        # Check skill match
        skill_match_score, matched_skills = self._calculate_skill_match(required_skills, freelancer_skills)
        
        if skill_match_score < 0.5:  # Requiring at least 50% skill match
            reasons.append(f"Skill match is too low ({skill_match_score:.0%})")
            passed = False
        else:
            reasons.append(f"Skills matched: {', '.join(matched_skills)} (Match: {skill_match_score:.0%})")

        # Check if pay rate is below freelancer's rate
        rate_concern = False
        if avg_pay_rate and freelancer_hourly_rate and avg_pay_rate < freelancer_hourly_rate:
            reasons.append(f"Pay rate (${avg_pay_rate}/hr) is below your rate (${freelancer_hourly_rate}/hr)")
            rate_concern = True

        # Calculate overall match score and determine match level
        match_score = self._calculate_overall_match_score(
            skill_match_score, client_rating, avg_pay_rate, 
            freelancer_hourly_rate, rate_concern
        )
        
        # Determine match level based on overall score
        if match_score >= 0.85:
            match_level = "EXCELLENT"
        elif match_score >= 0.70:
            match_level = "GREAT"
        elif match_score >= 0.55:
            match_level = "MODERATE"
        else:
            match_level = "LOW"

        # Generate recommendations based on match level
        if passed:
            if match_level == "EXCELLENT":
                recommendation = "Excellent match! This job is a perfect fit for your profile. Apply with confidence."
            elif match_level == "GREAT":
                recommendation = "Great match! This job is a strong fit for your profile. You can now generate a personalized proposal using AI."
            elif match_level == "MODERATE":
                recommendation = "Moderate match. Consider applying but highlight relevant experience and transferable skills."
            else:
                recommendation = "Low match. This job may not be the best fit, but you can still apply if interested."
        else:
            recommendation = "This job does not meet the minimum criteria. Consider looking for other opportunities."

        return {
            "result": "PASS" if passed else "FAIL",
            "reasons": reasons,
            "recommendation": recommendation,
            "skill_match_score": skill_match_score,
            "matched_skills": matched_skills,
            "match_level": match_level,
            "overall_match_score": match_score
        }

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
            # Check for exact matches first
            if req_skill in freelancer_skills:
                matched_skills.append(req_skill)
                continue
            
            # Check for semantic similarity only if we have valid text
            if len(req_skill.strip()) > 0 and any(len(skill.strip()) > 0 for skill in freelancer_skills):
                try:
                    req_doc = self.nlp(req_skill)
                    best_match_score = 0
                    best_match = None
                    
                    for free_skill in freelancer_skills:
                        if len(free_skill.strip()) > 0:
                            free_doc = self.nlp(free_skill)
                            # Only calculate similarity if both documents have vectors
                            if req_doc.has_vector and free_doc.has_vector:
                                similarity = req_doc.similarity(free_doc)
                                
                                if similarity > 0.8 and similarity > best_match_score:  # High similarity threshold
                                    best_match_score = similarity
                                    best_match = free_skill
                    
                    if best_match:
                        matched_skills.append(best_match)
                except Exception as e:
                    # If spaCy fails, continue with exact matching only
                    print(f"Warning: spaCy similarity calculation failed for '{req_skill}': {e}")
                    continue

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

    def _calculate_overall_match_score(self, skill_match_score: float, client_rating: float, 
                                     avg_pay_rate: float, freelancer_hourly_rate: float, 
                                     rate_concern: bool) -> float:
        """
        Calculate overall match score based on multiple factors.
        Returns a score between 0 and 1.
        """
        # Weight factors for different criteria
        skill_weight = 0.4
        client_weight = 0.25
        rate_weight = 0.25
        experience_weight = 0.1
        
        # Skill match component (0-1)
        skill_component = skill_match_score
        
        # Client rating component (0-1)
        client_component = 0.0
        if client_rating:
            if client_rating >= 4.8:
                client_component = 1.0
            elif client_rating >= 4.5:
                client_component = 0.9
            elif client_rating >= 4.0:
                client_component = 0.8
            elif client_rating >= 3.5:
                client_component = 0.6
            else:
                client_component = 0.3
        
        # Rate component (0-1)
        rate_component = 0.0
        if avg_pay_rate and freelancer_hourly_rate:
            rate_ratio = avg_pay_rate / freelancer_hourly_rate
            if rate_ratio >= 1.2:
                rate_component = 1.0  # Excellent rate
            elif rate_ratio >= 1.0:
                rate_component = 0.9  # Good rate
            elif rate_ratio >= 0.8:
                rate_component = 0.7  # Acceptable rate
            elif rate_ratio >= 0.6:
                rate_component = 0.5  # Low rate
            else:
                rate_component = 0.2  # Very low rate
            
            # Penalize if rate is below freelancer's rate
            if rate_concern:
                rate_component *= 0.8
        
        # Experience component (0-1) - simplified for now
        experience_component = 0.8  # Default to 0.8, can be enhanced later
        
        # Calculate weighted overall score
        overall_score = (
            skill_component * skill_weight +
            client_component * client_weight +
            rate_component * rate_weight +
            experience_component * experience_weight
        )
        
        return min(1.0, max(0.0, overall_score)) 