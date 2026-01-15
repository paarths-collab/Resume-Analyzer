import asyncio
import aiohttp
import os
import json
from typing import List, Dict
from google import genai
from google.genai import types
from datetime import datetime

# API Keys from environment (must be set in .env)
ADZUNA_RAPIDAPI_KEY = os.getenv('ADZUNA_RAPIDAPI_KEY', '')
OPENWEBNINJA_API_KEY = os.getenv('OPENWEBNINJA_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

class JobMatcher:
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=15)
    
    async def extract_resume_data(self, resume_text: str) -> Dict:
        """Extract skills, roles, and experience from resume using Gemini"""
        try:
            prompt = f"""
Analyze this resume and extract key information.

Resume:
{resume_text[:4000]}

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{"skills": ["skill1", "skill2"], "roles": ["role1", "role2"], "experience_years": 3, "location": "Remote", "seniority": "Mid"}}
"""
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt]
            )
            
            result_text = response.text.strip()
            
            # Clean JSON from markdown
            if '```' in result_text:
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            
            return json.loads(result_text.strip())
            
        except Exception as e:
            print(f"Gemini extraction error: {e}")
            return {
                "skills": ["Python", "JavaScript", "SQL"],
                "roles": ["Software Engineer", "Developer"],
                "experience_years": 2,
                "location": "Remote",
                "seniority": "Mid"
            }
    
    async def fetch_adzuna_jobs(self, session: aiohttp.ClientSession, skills: List[str], 
                                roles: List[str], location: str) -> List[Dict]:
        """Fetch jobs from Adzuna via RapidAPI"""
        try:
            query = roles[0] if roles else " ".join(skills[:3])
            url = "https://baskarm28-adzuna-v1.p.rapidapi.com/jobs/us/search/1"
            
            headers = {
                "x-rapidapi-key": ADZUNA_RAPIDAPI_KEY,
                "x-rapidapi-host": "baskarm28-adzuna-v1.p.rapidapi.com"
            }
            
            params = {
                "what": query,
                "results_per_page": "20"
            }
            
            async with session.get(url, headers=headers, params=params, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    jobs = []
                    for job in data.get('results', []):
                        jobs.append({
                            "source": "Adzuna",
                            "title": job.get('title', ''),
                            "company": job.get('company', {}).get('display_name', 'N/A'),
                            "location": job.get('location', {}).get('display_name', 'N/A'),
                            "description": job.get('description', '')[:500],
                            "url": job.get('redirect_url', ''),
                            "salary": job.get('salary_max', 0) or 0,
                            "posted_date": job.get('created', ''),
                            "remote": 'remote' in job.get('description', '').lower()
                        })
                    print(f"Adzuna: Found {len(jobs)} jobs")
                    return jobs
                else:
                    print(f"Adzuna: HTTP {resp.status}")
                    return []
                    
        except Exception as e:
            print(f"Adzuna error: {e}")
            return []
    
    async def fetch_openwebninja_jobs(self, session: aiohttp.ClientSession, skills: List[str], 
                                      roles: List[str], location: str) -> List[Dict]:
        """Fetch jobs from OpenWebNinja JSearch API"""
        try:
            query = f"{roles[0]} {location}" if roles else f"Software Engineer {location}"
            url = "https://api.openwebninja.com/jsearch/search"
            
            headers = {
                "x-api-key": OPENWEBNINJA_API_KEY,
                "Accept": "*/*"
            }
            
            params = {
                "query": query,
                "page": "1",
                "num_pages": "1",
                "country": "us",
                "language": "en",
                "date_posted": "month"
            }
            
            async with session.get(url, headers=headers, params=params, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    jobs = []
                    for job in data.get('data', [])[:20]:
                        jobs.append({
                            "source": "JSearch",
                            "title": job.get('job_title', ''),
                            "company": job.get('employer_name', 'N/A'),
                            "location": job.get('job_city', 'N/A') or job.get('job_country', 'N/A'),
                            "description": (job.get('job_description', '') or '')[:500],
                            "url": job.get('job_apply_link', '') or job.get('job_google_link', ''),
                            "salary": job.get('job_max_salary', 0) or 0,
                            "posted_date": job.get('job_posted_at_datetime_utc', ''),
                            "remote": job.get('job_is_remote', False)
                        })
                    print(f"JSearch: Found {len(jobs)} jobs")
                    return jobs
                else:
                    print(f"JSearch: HTTP {resp.status}")
                    text = await resp.text()
                    print(f"JSearch response: {text[:200]}")
                    return []
                    
        except Exception as e:
            print(f"JSearch error: {e}")
            return []
    
    async def fetch_arbeitnow_jobs(self, session: aiohttp.ClientSession, skills: List[str], 
                                   roles: List[str]) -> List[Dict]:
        """Fetch jobs from ArbeitNow API (free, no key needed)"""
        try:
            url = "https://www.arbeitnow.com/api/job-board-api"
            
            async with session.get(url, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    jobs = []
                    role_keywords = [r.lower() for r in roles]
                    skill_keywords = [s.lower() for s in skills]
                    
                    for job in data.get('data', [])[:50]:
                        title_lower = job.get('title', '').lower()
                        # Filter jobs matching skills/roles
                        if any(k in title_lower for k in role_keywords + skill_keywords):
                            jobs.append({
                                "source": "ArbeitNow",
                                "title": job.get('title', ''),
                                "company": job.get('company_name', 'N/A'),
                                "location": job.get('location', 'N/A'),
                                "description": job.get('description', '')[:500],
                                "url": job.get('url', ''),
                                "salary": 0,
                                "posted_date": job.get('created_at', ''),
                                "remote": job.get('remote', False)
                            })
                    print(f"ArbeitNow: Found {len(jobs)} jobs")
                    return jobs[:15]
                else:
                    print(f"ArbeitNow: HTTP {resp.status}")
                    return []
                    
        except Exception as e:
            print(f"ArbeitNow error: {e}")
            return []
    
    async def fetch_all_jobs(self, resume_data: Dict) -> List[Dict]:
        """Fetch jobs from all APIs in parallel"""
        skills = resume_data.get('skills', [])
        roles = resume_data.get('roles', [])
        location = resume_data.get('location', 'Remote')
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_adzuna_jobs(session, skills, roles, location),
                self.fetch_openwebninja_jobs(session, skills, roles, location),
                self.fetch_arbeitnow_jobs(session, skills, roles)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_jobs = []
            for result in results:
                if isinstance(result, list):
                    all_jobs.extend(result)
                elif isinstance(result, Exception):
                    print(f"API call failed: {result}")
            
            return all_jobs
    
    def calculate_match_score(self, job: Dict, resume_data: Dict) -> float:
        """Calculate match score between job and resume"""
        score = 0.0
        skills = [s.lower() for s in resume_data.get('skills', [])]
        roles = [r.lower() for r in resume_data.get('roles', [])]
        
        job_text = f"{job['title']} {job['description']}".lower()
        
        # Title match (30 points)
        for role in roles:
            role_words = role.split()
            if any(w in job['title'].lower() for w in role_words):
                score += 30
                break
        
        # Skills match (50 points max)
        matched_skills = sum(1 for skill in skills if skill.lower() in job_text)
        score += min(matched_skills * 7, 50)
        
        # Remote preference (10 points)
        if job.get('remote'):
            score += 10
        
        # Salary available (10 points)
        if job.get('salary', 0) > 0:
            score += 10
        
        return min(score, 100)
    
    def rank_jobs(self, jobs: List[Dict], resume_data: Dict) -> List[Dict]:
        """Rank and sort jobs by match score"""
        for job in jobs:
            job['match_score'] = self.calculate_match_score(job, resume_data)
        
        ranked = sorted(jobs, key=lambda x: x['match_score'], reverse=True)
        return ranked
    
    async def find_matching_jobs(self, resume_text: str) -> Dict:
        """Main entry point: Extract resume data, fetch jobs, rank results"""
        try:
            print("Extracting resume data...")
            resume_data = await self.extract_resume_data(resume_text)
            print(f"Resume data: {resume_data}")
            
            print("Fetching jobs from APIs...")
            all_jobs = await self.fetch_all_jobs(resume_data)
            print(f"Total jobs fetched: {len(all_jobs)}")
            
            print("Ranking jobs...")
            ranked_jobs = self.rank_jobs(all_jobs, resume_data)
            
            return {
                "success": True,
                "resume_data": resume_data,
                "total_jobs": len(ranked_jobs),
                "jobs": ranked_jobs[:50]
            }
            
        except Exception as e:
            print(f"Job matching error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "resume_data": {},
                "jobs": []
            }

# Create singleton instance
job_matcher = JobMatcher()