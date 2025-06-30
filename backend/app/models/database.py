import sqlite3
import json
from pathlib import Path
from datetime import datetime
import threading
import atexit

class Database:
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            try:
                db_path = Path("data/freelancer.db")
                db_path.parent.mkdir(parents=True, exist_ok=True)
                
                self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
                
                # Register cleanup on program exit
                atexit.register(self.cleanup)
                
                self.create_tables()
                self._initialized = True
            except sqlite3.Error as e:
                print(f"Database initialization error: {e}")
                raise
    
    def cleanup(self):
        """Cleanup database resources"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Ensure cleanup on object deletion"""
        self.cleanup()

    def _get_cursor(self):
        """Get a cursor with error handling"""
        try:
            return self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error getting cursor: {e}")
            # Try to reconnect
            self.conn = sqlite3.connect(str(Path("data/freelancer.db")), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            return self.conn.cursor()

    def create_tables(self):
        cursor = self._get_cursor()
        
        try:
            # Create freelancer profiles table with enhanced fields
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS freelancer_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                hourly_rate REAL NOT NULL,
                skills TEXT NOT NULL,
                experience_years INTEGER NOT NULL,
                bio TEXT,
                portfolio_url TEXT,
                timezone TEXT,
                availability_status TEXT DEFAULT 'Available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Create past projects table with enhanced fields
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS past_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                freelancer_id INTEGER,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                tech_stack TEXT NOT NULL,
                outcomes TEXT NOT NULL,
                project_url TEXT,
                client_name TEXT,
                project_duration TEXT,
                project_budget REAL,
                completion_date DATE,
                project_rating REAL,
                client_feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (freelancer_id) REFERENCES freelancer_profiles (id)
            )
            ''')

            # Create successful proposals table with enhanced fields
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS successful_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                freelancer_id INTEGER,
                job_title TEXT NOT NULL,
                job_url TEXT,
                proposal_text TEXT NOT NULL,
                client_response TEXT,
                proposal_status TEXT DEFAULT 'Submitted',
                submission_date DATE,
                response_date DATE,
                job_budget REAL,
                client_rating REAL,
                client_name TEXT,
                job_category TEXT,
                keywords_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (freelancer_id) REFERENCES freelancer_profiles (id)
            )
            ''')

            # Create job analysis history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                freelancer_id INTEGER,
                job_title TEXT NOT NULL,
                job_url TEXT,
                job_description TEXT,
                required_skills TEXT,
                client_rating REAL,
                avg_pay_rate REAL,
                analysis_result TEXT,
                analysis_reasons TEXT,
                recommendation TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (freelancer_id) REFERENCES freelancer_profiles (id)
            )
            ''')

            # Create scraped job data table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT NOT NULL,
                job_url TEXT UNIQUE,
                job_description TEXT,
                required_skills TEXT,
                client_name TEXT,
                client_rating REAL,
                client_total_jobs INTEGER,
                client_total_hires INTEGER,
                client_avg_review REAL,
                budget_range TEXT,
                avg_pay_rate REAL,
                project_duration TEXT,
                job_category TEXT,
                posted_date DATE,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            raise
        finally:
            cursor.close()

    def add_freelancer_profile(self, name, email, hourly_rate, skills, experience_years, bio=None, portfolio_url=None, timezone=None):
        cursor = self._get_cursor()
        try:
            cursor.execute('''
            INSERT INTO freelancer_profiles (name, email, hourly_rate, skills, experience_years, bio, portfolio_url, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, email, hourly_rate, json.dumps(skills), experience_years, bio, portfolio_url, timezone))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding freelancer profile: {e}")
            self.conn.rollback()
            raise
        finally:
            cursor.close()

    def update_freelancer_profile(self, freelancer_id, **kwargs):
        cursor = self._get_cursor()
        try:
            update_fields = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['name', 'email', 'hourly_rate', 'experience_years', 'bio', 'portfolio_url', 'timezone', 'availability_status']:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
                elif key == 'skills':
                    update_fields.append("skills = ?")
                    values.append(json.dumps(value))
            
            if update_fields:
                update_fields.append("updated_at = ?")
                values.append(datetime.now())
                values.append(freelancer_id)
                
                query = f"UPDATE freelancer_profiles SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, values)
                self.conn.commit()
                return cursor.rowcount > 0
            return False
        except sqlite3.Error as e:
            print(f"Error updating freelancer profile: {e}")
            self.conn.rollback()
            raise
        finally:
            cursor.close()

    def _safe_float(self, value, default=0.0):
        """Safely convert a value to float."""
        try:
            if value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    def _safe_int(self, value, default=0):
        """Safely convert a value to int."""
        try:
            if value is None:
                return default
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_freelancer_profile(self, freelancer_id):
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM freelancer_profiles WHERE id = ?', (freelancer_id,))
            profile = cursor.fetchone()
            if profile:
                return {
                    'id': profile[0],
                    'name': profile[1],
                    'email': profile[2] if len(profile) > 2 else None,
                    'hourly_rate': self._safe_float(profile[3]),
                    'skills': self._parse_skills(profile[4]),
                    'experience_years': self._safe_int(profile[5]) if len(profile) > 5 else 0,
                    'bio': profile[6] if len(profile) > 6 else None,
                    'portfolio_url': profile[7] if len(profile) > 7 else None,
                    'timezone': profile[8] if len(profile) > 8 else None,
                    'availability_status': profile[9] if len(profile) > 9 else 'Available',
                    'created_at': profile[10] if len(profile) > 10 else None,
                    'updated_at': profile[11] if len(profile) > 11 else None
                }
            return None
        except sqlite3.Error as e:
            print(f"Error getting freelancer profile: {e}")
            return None
        finally:
            cursor.close()

    def add_past_project(self, freelancer_id, title, description, tech_stack, outcomes, project_url=None, 
                        client_name=None, project_duration=None, project_budget=None, completion_date=None, 
                        project_rating=None, client_feedback=None):
        cursor = self._get_cursor()
        try:
            cursor.execute('''
            INSERT INTO past_projects (freelancer_id, title, description, tech_stack, outcomes, project_url, 
                                    client_name, project_duration, project_budget, completion_date, 
                                    project_rating, client_feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (freelancer_id, title, description, json.dumps(tech_stack), outcomes, project_url, 
                client_name, project_duration, project_budget, completion_date, project_rating, client_feedback))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding past project: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    def get_past_projects(self, freelancer_id):
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM past_projects WHERE freelancer_id = ? ORDER BY completion_date DESC', (freelancer_id,))
            projects = cursor.fetchall()
            return [{
                'id': project[0],
                'freelancer_id': project[1],
                'title': project[2],
                'description': project[3],
                'tech_stack': self._parse_json_field(project[4]),
                'outcomes': project[5],
                'project_url': project[6],
                'client_name': project[7],
                'project_duration': project[8],
                'project_budget': self._safe_float(project[9]),
                'completion_date': project[10],
                'project_rating': self._safe_float(project[11]),
                'client_feedback': project[12],
                'created_at': project[13]
            } for project in projects]
        except sqlite3.Error as e:
            print(f"Error getting past projects: {e}")
            return []
        finally:
            cursor.close()

    def add_successful_proposal(self, freelancer_id, job_title, proposal_text, job_url=None, 
                            client_response=None, proposal_status='Submitted', submission_date=None,
                            response_date=None, job_budget=None, client_rating=None, client_name=None,
                            job_category=None, keywords_used=None):
        cursor = self._get_cursor()
        try:
            # Format keywords_used to string if it's a list
            if isinstance(keywords_used, list):
                keywords_used = ', '.join(keywords_used) if keywords_used else None
            
            cursor.execute('''
            INSERT INTO successful_proposals (freelancer_id, job_title, job_url, proposal_text, client_response,
                                        proposal_status, submission_date, response_date, job_budget,
                                        client_rating, client_name, job_category, keywords_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (freelancer_id, job_title, job_url, proposal_text, client_response, proposal_status,
                submission_date, response_date, job_budget, client_rating, client_name,
                job_category, keywords_used))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding successful proposal: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    def get_successful_proposals(self, freelancer_id):
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM successful_proposals WHERE freelancer_id = ? ORDER BY created_at DESC', (freelancer_id,))
            proposals = cursor.fetchall()
            return [{
                'id': proposal[0],
                'freelancer_id': proposal[1],
                'job_title': proposal[2],
                'job_url': proposal[3],
                'proposal_text': proposal[4],
                'client_response': proposal[5],
                'proposal_status': proposal[6],
                'submission_date': proposal[7],
                'response_date': proposal[8],
                'job_budget': self._safe_float(proposal[9]),
                'client_rating': self._safe_float(proposal[10]),
                'client_name': proposal[11],
                'job_category': proposal[12],
                'keywords_used': self._format_keywords_used(proposal[13]),
                'created_at': proposal[14]
            } for proposal in proposals]
        except sqlite3.Error as e:
            print(f"Error getting successful proposals: {e}")
            return []
        finally:
            cursor.close()

    def _format_keywords_used(self, keywords_data):
        """Format keywords_used field to be a string"""
        if not keywords_data:
            return None
        try:
            parsed = json.loads(keywords_data)
            if isinstance(parsed, list):
                return ', '.join(parsed) if parsed else None
            elif isinstance(parsed, str):
                return parsed
            else:
                return str(parsed) if parsed else None
        except (json.JSONDecodeError, TypeError):
            return keywords_data if keywords_data else None

    def add_job_analysis(self, freelancer_id, job_title, job_url, job_description, required_skills,
                        client_rating, avg_pay_rate, analysis_result, analysis_reasons, recommendation):
        cursor = self._get_cursor()
        try:
            cursor.execute('''
            INSERT INTO job_analysis_history (freelancer_id, job_title, job_url, job_description, required_skills,
                                           client_rating, avg_pay_rate, analysis_result, analysis_reasons, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (freelancer_id, job_title, job_url, job_description, json.dumps(required_skills),
                 client_rating, avg_pay_rate, analysis_result, json.dumps(analysis_reasons), recommendation))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding job analysis: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    def add_scraped_job(self, job_title, job_url, job_description, required_skills, client_name,
                       client_rating, client_total_jobs, client_total_hires, client_avg_review,
                       budget_range, avg_pay_rate, project_duration, job_category, posted_date):
        cursor = self._get_cursor()
        try:
            cursor.execute('''
            INSERT INTO scraped_jobs (job_title, job_url, job_description, required_skills, client_name,
                                    client_rating, client_total_jobs, client_total_hires, client_avg_review,
                                    budget_range, avg_pay_rate, project_duration, job_category, posted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (job_title, job_url, job_description, json.dumps(required_skills), client_name,
                 client_rating, client_total_jobs, client_total_hires, client_avg_review,
                 budget_range, avg_pay_rate, project_duration, job_category, posted_date))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding scraped job: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    def get_scraped_jobs(self, limit=50):
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM scraped_jobs ORDER BY scraped_at DESC LIMIT ?', (limit,))
            jobs = cursor.fetchall()
            return [{
                'id': job[0],
                'job_title': job[1],
                'job_url': job[2],
                'job_description': job[3],
                'required_skills': self._parse_json_field(job[4]),
                'client_name': job[5],
                'client_rating': self._safe_float(job[6]),
                'client_total_jobs': self._safe_int(job[7]),
                'client_total_hires': self._safe_int(job[8]),
                'client_avg_review': self._safe_float(job[9]),
                'budget_range': job[10],
                'avg_pay_rate': self._safe_float(job[11]),
                'project_duration': job[12],
                'job_category': job[13],
                'posted_date': job[14],
                'scraped_at': job[15]
            } for job in jobs]
        except sqlite3.Error as e:
            print(f"Error getting scraped jobs: {e}")
            return []
        finally:
            cursor.close()

    def get_all_freelancer_profiles(self):
        cursor = self._get_cursor()
        try:
            cursor.execute('SELECT * FROM freelancer_profiles ORDER BY name')
            profiles = cursor.fetchall()
            return [{
                'id': profile[0],
                'name': profile[1],
                'email': profile[2],
                'hourly_rate': self._safe_float(profile[3]),
                'skills': self._parse_skills(profile[4]),
                'experience_years': self._safe_int(profile[5]),
                'bio': profile[6],
                'portfolio_url': profile[7],
                'timezone': profile[8],
                'availability_status': profile[9],
                'created_at': profile[10],
                'updated_at': profile[11]
            } for profile in profiles]
        except sqlite3.Error as e:
            print(f"Error getting all freelancer profiles: {e}")
            return []
        finally:
            cursor.close()

    def _parse_skills(self, skills_data):
        """Parse skills data from JSON or string format"""
        if not skills_data:
            return []
        try:
            if isinstance(skills_data, str):
                # Try to parse as JSON first
                try:
                    return json.loads(skills_data)
                except json.JSONDecodeError:
                    # If not JSON, split by comma
                    return [s.strip() for s in skills_data.split(',') if s.strip()]
            elif isinstance(skills_data, (list, tuple)):
                return list(skills_data)
            else:
                return []
        except Exception as e:
            print(f"Error parsing skills data: {e}")
            return []

    def _parse_json_field(self, json_data):
        """Safely parse JSON field data"""
        if not json_data:
            return None
        try:
            return json.loads(json_data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing JSON data: {e}")
            return None

    def delete_all_profiles_and_related(self):
        cursor = self._get_cursor()
        try:
            # Delete related data first due to foreign key constraints
            cursor.execute('DELETE FROM past_projects')
            cursor.execute('DELETE FROM successful_proposals')
            cursor.execute('DELETE FROM job_analysis_history')
            cursor.execute('DELETE FROM freelancer_profiles')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting all profiles and related data: {e}")
            self.conn.rollback()
            raise
        finally:
            cursor.close()

    def delete_freelancer_profile(self, freelancer_id):
        cursor = self._get_cursor()
        try:
            # Delete related data first due to foreign key constraints
            cursor.execute('DELETE FROM past_projects WHERE freelancer_id = ?', (freelancer_id,))
            cursor.execute('DELETE FROM successful_proposals WHERE freelancer_id = ?', (freelancer_id,))
            cursor.execute('DELETE FROM job_analysis_history WHERE freelancer_id = ?', (freelancer_id,))
            cursor.execute('DELETE FROM freelancer_profiles WHERE id = ?', (freelancer_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting freelancer profile and related data: {e}")
            self.conn.rollback()
            return False
        finally:
            cursor.close() 