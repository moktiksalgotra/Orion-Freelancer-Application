import requests
import logging
import os
from typing import List, Dict, Optional
import time
import random
import re
import spacy

class UpworkScraper:
    def __init__(self):
        # Get API key from environment variable or use a default one
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', 'e0d62349cfmsh4d798dd65fd8115p185499jsndffc919977fe')
        # Using RapidAPI service for Upwork jobs
        self.rapidapi_host = "upwork-jobs-api2.p.rapidapi.com"
        self.base_url = "https://upwork-jobs-api2.p.rapidapi.com"
        
        # Rate limiting settings
        self.min_delay = 5  # Minimum delay between requests in seconds (increased from 2)
        self.max_delay = 15  # Maximum delay between requests in seconds (increased from 10)
        self.last_request_time = 0

        try:
            self.nlp = spacy.load('en_core_web_sm')
        except Exception:
            os.system('python -m spacy download en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')

    def _rate_limit(self):
        """Implement rate limiting to avoid 429 errors"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            logging.info(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _make_request_with_retry(self, url: str, headers: dict, params: dict = None, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with exponential backoff and retry logic"""
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logging.warning(f"Rate limited (429). Waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                else:
                    logging.warning(f"API returned status {response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                    
            except requests.exceptions.RequestException as e:
                logging.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        
        return None

    def search_jobs(self, keywords: List[str], max_jobs: int = 1, category_filter: str = None) -> List[Dict]:
        """
        Search for jobs using RapidAPI Upwork Jobs API. Returns professional error if API is unavailable.
        """
        all_jobs = []
        
        for keyword in keywords:
            logging.info(f"Searching for keyword: {keyword}")
            jobs = self._search_jobs_primary(keyword, max_jobs, category_filter)
            
            if jobs:
                all_jobs.extend(jobs)
                logging.info(f"Successfully found {len(jobs)} jobs for keyword '{keyword}'")
            else:
                logging.warning(f"No jobs found for keyword '{keyword}' - API may be rate limited or unavailable")
            
            time.sleep(2)  # Delay between keywords
        
        if not all_jobs:
            logging.error("No jobs retrieved from RapidAPI or any source. Returning empty list. Possible causes:")
            logging.error("- API rate limit exceeded (429 error)")
            logging.error("- Invalid or expired API key")
            logging.error("- Network connectivity issues")
            logging.error("- RapidAPI service temporarily unavailable")
            return []
        
        return all_jobs

    def _search_jobs_primary(self, keyword: str, max_jobs: int, category_filter: str = None) -> List[Dict]:
        """
        Search using primary RapidAPI service
        """
        url = f"{self.base_url}/active-freelance-1h"
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.rapidapi_host
        }
        params = {
            "limit": max_jobs
        }
        
        response = self._make_request_with_retry(url, headers, params)
        
        if response is None:
            logging.error("Failed to get response from primary API after all retries")
            return []
        
        try:
            data = response.json()
            print("RAW API DATA:", data)  # Debug print to show raw API response
            # New API returns a list directly, not a dict with 'data' key
            if isinstance(data, list):
                jobs = data
            else:
                jobs = data.get("data", [])
            logging.info(f"Fetched {len(jobs)} jobs from API for keyword '{keyword}' (no filtering applied).")
            jobs = jobs[:max_jobs]
            return self._map_api_jobs(jobs)
        except Exception as e:
            logging.error(f"Error processing response from primary API: {e}")
            return []

    def _clean_job_title(self, title: str) -> str:
        # Use spaCy to extract the main noun chunk or just clean up extra symbols
        doc = self.nlp(title)
        noun_chunks = list(doc.noun_chunks)
        if noun_chunks:
            return noun_chunks[0].text.strip()
        return title.strip()

    def _clean_job_description(self, desc: str) -> str:
        # Use spaCy to extract the most relevant sentences (first 2-3)
        doc = self.nlp(desc)
        sentences = list(doc.sents)
        if len(sentences) >= 2:
            return ' '.join([sent.text.strip() for sent in sentences[:2]])
        elif sentences:
            return sentences[0].text.strip()
        return desc.strip()

    def _extract_pay_rate(self, job: dict) -> float:
        # Try to extract a numeric pay rate from various fields using regex
        if 'project_budget_hourly_min' in job and 'project_budget_hourly_max' in job:
            try:
                min_rate = float(job['project_budget_hourly_min'])
                max_rate = float(job['project_budget_hourly_max'])
                return (min_rate + max_rate) / 2
            except Exception:
                pass
        if 'project_budget_total' in job:
            try:
                return float(job['project_budget_total'])
            except Exception:
                pass
        # Fallback: search for $amount in description
        desc = job.get('description_text', '')
        match = re.search(r'\$(\d+[\.,]?\d*)', desc)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except Exception:
                pass
        return 0.0

    def _map_api_jobs(self, api_jobs: List[Dict]) -> List[Dict]:
        """
        Map API response to our expected job format, with spaCy/regex cleaning
        """
        mapped_jobs = []
        for job in api_jobs:
            try:
                # Extract skills as a list of strings
                skills = []
                if isinstance(job.get('skills'), list):
                    skills = [skill.get('name', '') for skill in job.get('skills', []) if skill.get('name')]
                # Clean job title and description
                job_title = self._clean_job_title(job.get('title', ''))
                job_description = self._clean_job_description(job.get('description_text', ''))
                # Extract pay rate
                avg_pay_rate = self._extract_pay_rate(job)
                # Extract client information
                client_name = self._extract_client_name_new(job)
                client_rating = self._extract_client_rating_new(job)
                mapped_job = {
                    'job_title': job_title,
                    'job_url': job.get('url', ''),
                    'job_description': job_description,
                    'required_skills': skills,
                    'client_name': client_name,
                    'client_rating': client_rating,
                    'client_total_jobs': job.get('client_open_jobs', 0),
                    'client_total_hires': job.get('client_jobs_with_hires', 0),
                    'client_avg_review': client_rating,
                    'budget_range': self._extract_budget_range_new(job),
                    'avg_pay_rate': avg_pay_rate,
                    'project_duration': self._extract_duration_new(job),
                    'job_category': job.get('category', ''),
                    'posted_date': job.get('date_posted', '')
                }
                mapped_jobs.append(mapped_job)
            except Exception as e:
                logging.error(f"Error mapping job: {e}")
                continue
        return mapped_jobs

    def _extract_budget_range_new(self, job: Dict) -> str:
        """Extract budget range from new API format"""
        # Check for hourly budget
        hourly_min = job.get('project_budget_hourly_min')
        hourly_max = job.get('project_budget_hourly_max')
        
        if hourly_min and hourly_max:
            currency = job.get('project_budget_currency', 'USD')
            return f"${hourly_min}-${hourly_max}/{currency}/hr"
        
        # Check for total budget
        total_budget = job.get('project_budget_total')
        if total_budget:
            currency = job.get('project_budget_currency', 'USD')
            return f"${total_budget} {currency}"
        
        return 'N/A'

    def _extract_avg_pay_rate_new(self, job: Dict) -> float:
        """Extract average pay rate from new API format"""
        hourly_min = job.get('project_budget_hourly_min')
        hourly_max = job.get('project_budget_hourly_max')
        
        if hourly_min and hourly_max:
            try:
                return (float(hourly_min) + float(hourly_max)) / 2
            except (ValueError, TypeError):
                pass
        
        return 0.0

    def _extract_client_name_new(self, job: Dict) -> str:
        """Extract client name from new API format"""
        # The new API doesn't provide client name directly
        # We'll use a placeholder or try to extract from other fields
        return 'Client'  # Placeholder since API doesn't provide client name

    def _extract_client_rating_new(self, job: Dict) -> float:
        """Extract client rating from new API format"""
        client_score = job.get('client_score')
        if client_score:
            try:
                return float(client_score)
            except (ValueError, TypeError):
                pass
        return 0.0

    def _extract_duration_new(self, job: Dict) -> str:
        """Extract project duration from new API format"""
        engagement = job.get('engagement_duration', {})
        if isinstance(engagement, dict):
            return engagement.get('label', '')
        return ''

    def scrape_job_from_url(self, url: str) -> Optional[Dict]:
        """
        Scrape a specific job from URL using RapidAPI
        """
        try:
            # Extract job ID from URL
            job_id_match = re.search(r'/jobs/~([a-zA-Z0-9_]+)', url)
            if not job_id_match:
                return None
            
            job_id = job_id_match.group(1)
            
            # Try to get job details from API
            api_url = f"{self.base_url}/job/{job_id}"
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": self.rapidapi_host
            }
            
            response = self._make_request_with_retry(api_url, headers)
            
            if response is None:
                logging.error("Failed to get job details from API after all retries")
                return None
            
            job_data = response.json()
            return self._map_api_jobs([job_data])[0] if job_data else None
                
        except Exception as e:
            logging.error(f"Error scraping job from URL: {e}")
            return None