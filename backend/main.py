# from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse
# from pydantic import BaseModel
# from google import genai
# from google.genai import types
# import os
# import re
# from dotenv import load_dotenv
# from pathlib import Path

# # Load environment variables from .env file
# load_dotenv()

# # Get the base directory (parent of backend folder)
# BASE_DIR = Path(__file__).resolve().parent.parent

# app = FastAPI()



# # Setup templates
# templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Configure Gemini API (new package)
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     print("Warning: GEMINI_API_KEY environment variable not set")
# else:
#     client = genai.Client(api_key=GEMINI_API_KEY)
#     print(f"✅ Gemini API configured successfully")

# class AnalysisResponse(BaseModel):
#     score: int
#     score_explanation: str
#     summary: str
#     improvements: str
#     job_roles: str
#     ats_score: int
#     keyword_score: int
#     format_score: int
#     header_score: int
#     readability_score: int

# def parse_analysis(response_text: str) -> dict:
#     """Parse the Gemini response into structured data"""
#     # Extract score (looking for a number out of 100)
#     match = re.search(
#         r'(?:score|rating)\s*[:\-]?\s*(\d{1,3})',
#         response_text,
#         re.IGNORECASE
#     )

#     if match:
#         score = int(match.group(1))
#         score = max(0, min(score, 100))
#     else:
#         score = 0
    
#     # Extract sections based on headers
#     sections = {
#         'score_explanation': '',
#         'summary': '',
#         'improvements': '',
#         'job_roles': ''
#     }
    
#     # Split by common section headers
#     score_patterns = [r'(?:score|rating|match).*?explanation', r'score analysis', r'match score']
#     summary_patterns = [r'(?:resume )?summary', r'candidate profile', r'overview', r'professional summary']
#     improvement_patterns = [r'improvements?', r'recommendations?', r'suggestions?', r'areas? (?:to|for) improve', r'how to improve']
#     job_role_patterns = [r'suitable.*?(?:job|role|position)s?', r'job.*?roles?', r'recommended.*?(?:job|role|position)s?', r'career.*?(?:path|option|suggestion)s?']
    
#     text_lower = response_text.lower()
    
#     # Try to find section boundaries
#     for pattern in score_patterns:
#         match = re.search(pattern, text_lower)
#         if match:
#             start = match.end()
#             next_section = re.search(r'(?:summary|improvements?|recommendations?)', text_lower[start:])
#             end = start + next_section.start() if next_section else start + 500
#             sections['score_explanation'] = response_text[start:end].strip(' :\n-*#')
#             break
    
#     for pattern in summary_patterns:
#         match = re.search(pattern, text_lower)
#         if match:
#             start = match.end()
#             next_section = re.search(r'(?:improvements?|recommendations?|suggestions?)', text_lower[start:])
#             end = start + next_section.start() if next_section else start + 800
#             sections['summary'] = response_text[start:end].strip(' :\n-*#')
#             break
    
#     for pattern in improvement_patterns:
#         match = re.search(pattern, text_lower)
#         if match:
#             start = match.end()
#             next_section = re.search(r'(?:suitable|job roles?|recommended roles?|career)', text_lower[start:])
#             end = start + next_section.start() if next_section else len(response_text)
#             sections['improvements'] = response_text[start:end].strip(' :\n-*#')
#             break
    
#     for pattern in job_role_patterns:
#         match = re.search(pattern, text_lower)
#         if match:
#             start = match.end()
#             sections['job_roles'] = response_text[start:].strip(' :\n-*#')
#             break
    
#     # Fallback: if sections are empty, try splitting by numbered sections
#     if not any(sections.values()):
#         parts = re.split(r'\n(?=\d\.|\*\*)', response_text)
#         if len(parts) >= 4:
#             sections['score_explanation'] = parts[0]
#             sections['summary'] = parts[1] if len(parts) > 1 else ""
#             sections['improvements'] = '\n'.join(parts[2:4]) if len(parts) > 2 else ""
#             sections['job_roles'] = '\n'.join(parts[4:]) if len(parts) > 4 else ""
#         else:
#             # Last resort: split by paragraphs
#             paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
#             if len(paragraphs) >= 4:
#                 sections['score_explanation'] = paragraphs[0]
#                 sections['summary'] = paragraphs[1]
#                 sections['improvements'] = '\n\n'.join(paragraphs[2:4])
#                 sections['job_roles'] = '\n\n'.join(paragraphs[4:]) if len(paragraphs) > 4 else "Based on your skills, consider roles in software engineering, data science, or related technical fields."
#             else:
#                 sections['score_explanation'] = "Resume analyzed against job requirements"
#                 sections['summary'] = response_text[:500] if len(response_text) > 500 else response_text
#                 sections['improvements'] = "Consider tailoring your resume to highlight relevant skills mentioned in the job description"
#                 sections['job_roles'] = "Software Engineer, Data Analyst, Technical Consultant"
    
#     # Extract ATS scores
#     ats_scores = {
#         'ats_score': 0,
#         'keyword_score': 0,
#         'format_score': 0,
#         'header_score': 0,
#         'readability_score': 0
#     }
    
#     # Look for ATS score patterns
#     ats_patterns = [
#         (r'ats\s*(?:score|compatibility)?\s*[:\-]?\s*(\d{1,3})', 'ats_score'),
#         (r'keyword\s*(?:score|match)?\s*[:\-]?\s*(\d{1,3})', 'keyword_score'),
#         (r'format(?:ting)?\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'format_score'),
#         (r'(?:section\s*)?header\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'header_score'),
#         (r'readability\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'readability_score'),
#     ]
    
#     for pattern, key in ats_patterns:
#         match = re.search(pattern, response_text, re.IGNORECASE)
#         if match:
#             val = int(match.group(1))
#             ats_scores[key] = max(0, min(val, 100))
    
#     # If ATS score not found, derive from main score
#     if ats_scores['ats_score'] == 0:
#         ats_scores['ats_score'] = score
#     if ats_scores['keyword_score'] == 0:
#         ats_scores['keyword_score'] = score
#     if ats_scores['format_score'] == 0:
#         ats_scores['format_score'] = score
#     if ats_scores['header_score'] == 0:
#         ats_scores['header_score'] = score
#     if ats_scores['readability_score'] == 0:
#         ats_scores['readability_score'] = score
    
#     return {
#         'score': score,
#         'score_explanation': sections['score_explanation'][:600] if sections['score_explanation'] else "Resume evaluated based on job requirements",
#         'summary': sections['summary'][:1200] if sections['summary'] else "Professional background and qualifications reviewed",
#         'improvements': sections['improvements'][:3000] if sections['improvements'] else "Focus on highlighting relevant experience and skills that match the job description",
#         'job_roles': sections['job_roles'][:1500] if sections['job_roles'] else "Consider roles aligned with your technical expertise and experience",
#         'ats_score': ats_scores['ats_score'],
#         'keyword_score': ats_scores['keyword_score'],
#         'format_score': ats_scores['format_score'],
#         'header_score': ats_scores['header_score'],
#         'readability_score': ats_scores['readability_score']
#     }

# @app.post("/analyze", response_model=AnalysisResponse)
# async def analyze_resume(
#     resume: UploadFile = File(...),
#     job_description: str = Form(...)
# ):
#     """Analyze resume against job description using Gemini"""
    
#     if not GEMINI_API_KEY:
#         raise HTTPException(
#             status_code=500, 
#             detail="GEMINI_API_KEY environment variable not set. Please set it before running the server."
#         )
    
#     # Read PDF file
#     pdf_content = await resume.read()
    
#     # Verify it's a PDF
#     if not resume.filename.lower().endswith('.pdf'): # type: ignore
#         raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
#     # Create prompt for Gemini
#     prompt = f"""Analyze this resume PDF against the provided job description and provide a detailed evaluation.

# JOB DESCRIPTION:
# {job_description}

# Please provide your analysis in the following format:

# SCORE: [Provide a numerical score from 0-100 indicating how well the resume matches the job requirements]

# SCORE EXPLANATION: [Provide 2-3 sentences explaining why you gave this score, mentioning key matching and missing elements]

# ATS SCORES: [Provide these specific ATS compatibility metrics, each as a number from 0-100]
# - ATS SCORE: [Overall ATS compatibility score]
# - KEYWORD SCORE: [How well the resume keywords match the job description]
# - FORMAT SCORE: [How ATS-friendly the resume formatting is]
# - HEADER SCORE: [How well standard section headers are used]
# - READABILITY SCORE: [How easy the resume is to parse]

# SUMMARY: [Provide a 3-4 sentence professional summary of the candidate's background, key skills, and experience level]

# IMPROVEMENTS: [Provide 7-10 specific, actionable bullet points on how to improve this resume for this particular job. Be comprehensive and detailed. Include suggestions about:
# - Keywords to add
# - Skills to highlight
# - Experience to emphasize
# - Formatting suggestions
# - Content gaps to fill]

# SUITABLE JOB ROLES: [Based on the candidate's skills and experience shown in the resume, suggest 5-8 job roles/titles that would be a good fit. For each role, briefly explain why (1 sentence). Format as a list.]

# Make your analysis specific, actionable, and comprehensive."""

#     try:
#         # Use new Gemini API
#         response = client.models.generate_content(
#             model='gemini-2.5-flash-lite',
#             contents=[
#                 types.Part.from_bytes(
#                     data=pdf_content,
#                     mime_type='application/pdf'
#                 ),
#                 prompt
#             ]
#         )
        
#         response_text = response.text
        
#         # Parse the response
#         analysis = parse_analysis(response_text) # type: ignore
        
#         return AnalysisResponse(**analysis)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

# @app.get("/", response_class=HTMLResponse)
# @app.get("/dashboard", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     return templates.TemplateResponse("dashboard.html", {
#         "request": request,
#         "page_title": "Dashboard",
#         "active_page": "dashboard"
#     })

# @app.get("/analysis", response_class=HTMLResponse)
# async def analysis_page(request: Request):
#     return templates.TemplateResponse("analysis.html", {
#         "request": request,
#         "page_title": "Analysis",
#         "active_page": "analysis"
#     })

# @app.get("/chat", response_class=HTMLResponse)
# async def chat_page(request: Request):
#     return templates.TemplateResponse("chat.html", {
#         "request": request,
#         "page_title": "AI Chat",
#         "active_page": "chat"
#     })

# class ChatRequest(BaseModel):
#     message: str
#     options: list[str] = []

# class ChatResponse(BaseModel):
#     response: str

# @app.post("/chat", response_model=ChatResponse)
# async def chat_with_ai(
#     resume: UploadFile = File(None),
#     message: str = Form(...),
#     options: str = Form("")
# ):
#     """Chat endpoint for conversational AI responses"""
    
#     if not GEMINI_API_KEY:
#         raise HTTPException(
#             status_code=500, 
#             detail="GEMINI_API_KEY not configured"
#         )
    
#     # Parse options (comma-separated)
#     option_list = [o.strip() for o in options.split(',') if o.strip()]
    
#     # Build context based on selected options
#     context_parts = []
#     if 'general' in option_list:
#         context_parts.append("- Provide general resume feedback")
#     if 'ats' in option_list:
#         context_parts.append("- Check ATS (Applicant Tracking System) compatibility")
#     if 'keywords' in option_list:
#         context_parts.append("- Analyze keyword usage and suggest improvements")
#     if 'formatting' in option_list:
#         context_parts.append("- Review formatting and layout")
#     if 'skills' in option_list:
#         context_parts.append("- Identify skills gaps")
#     if 'experience' in option_list:
#         context_parts.append("- Analyze experience section")
    
#     options_context = '\n'.join(context_parts) if context_parts else "- General resume assistance"
    
#     # Build prompt
#     prompt = f"""You are a helpful AI resume assistant having a conversation with a user.

# User's message: {message}

# Focus areas (if resume provided):
# {options_context}

# Instructions:
# - Respond in a friendly, conversational tone
# - Keep responses concise but helpful
# - Use simple dashes (-) for bullet points, NEVER use asterisks (*)
# - Don't use markdown headers, bold text (**), or any markdown formatting
# - If no resume is provided, still help with general resume advice based on the user's question
# - If analyzing a resume for ATS compatibility, ALWAYS start your response with "ATS Score: X/100" where X is your estimated ATS compatibility score, then explain your reasoning
# - Format the ATS score on its own line at the very beginning"""

#     try:
#         contents = []
        
#         # Add resume if provided
#         if resume and resume.filename:
#             pdf_content = await resume.read()
#             contents.append(
#                 types.Part.from_bytes(
#                     data=pdf_content,
#                     mime_type='application/pdf'
#                 )
#             )
        
#         contents.append(prompt)
        
#         response = client.models.generate_content(
#             model='gemini-2.5-flash-lite',
#             contents=contents
#         )
        
#         # Clean up asterisks from response
#         clean_response = response.text.replace('*', '')
        
#         return ChatResponse(response=clean_response)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# @app.get("/health")
# async def health_check():
#     """Check if API key is configured"""
#     return {
#         "status": "healthy",
#         "gemini_configured": bool(GEMINI_API_KEY)
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import HTMLResponse, FileResponse
# from pydantic import BaseModel
# from google import genai
# from google.genai import types
# import os
# import re
# from dotenv import load_dotenv
# from pathlib import Path

# # Import auth modules
# from backend.auth_models import (
#     SignupRequest, LoginRequest, ForgotPasswordRequest, 
#     ResetPasswordRequest, LoginResponse, MessageResponse, UserResponse
# )
# from backend.auth_service import auth_service
# from backend.auth_middleware import get_current_user, get_optional_user
# from backend.database import get_db_cursor

# load_dotenv()

# BASE_DIR = Path(__file__).resolve().parent.parent
# FRONTEND_DIR = BASE_DIR / "frontend"

# app = FastAPI()

# templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Configure Gemini API
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     print("Warning: GEMINI_API_KEY environment variable not set")
# else:
#     client = genai.Client(api_key=GEMINI_API_KEY)
#     print(f"✅ Gemini API configured successfully")

# # ==================== AUTH ENDPOINTS ====================

# @app.post("/api/auth/signup", response_model=UserResponse)
# async def signup(request: SignupRequest):
#     """Create new user account"""
#     try:
#         user = auth_service.signup(
#             email=request.email,
#             password=request.password,
#             full_name=request.full_name
#         )
#         return UserResponse(
#             id=user['id'],
#             email=user['email'],
#             full_name=user.get('full_name')
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

# @app.post("/api/auth/login", response_model=LoginResponse)
# async def login(request: LoginRequest):
#     """Authenticate user and create session"""
#     try:
#         result = auth_service.login(
#             email=request.email,
#             password=request.password
#         )
#         return LoginResponse(**result)
#     except ValueError as e:
#         raise HTTPException(status_code=401, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# @app.get("/api/auth/me", response_model=UserResponse)
# async def get_me(current_user: dict = Depends(get_current_user)):
#     """Get current authenticated user"""
#     return UserResponse(**current_user)

# @app.post("/api/auth/logout", response_model=MessageResponse)
# async def logout(current_user: dict = Depends(get_current_user)):
#     """Logout and invalidate session"""
#     # Extract token from request (handled in dependency)
#     return MessageResponse(message="Logged out successfully")

# @app.post("/api/auth/forgot-password", response_model=MessageResponse)
# async def forgot_password(request: ForgotPasswordRequest):
#     """Request password reset token"""
#     try:
#         result = auth_service.request_password_reset(request.email)
#         # In production, send email with token
#         # For development, return token in response
#         return MessageResponse(
#             message=f"Password reset token generated. Token: {result['token']} (In production, this would be emailed)"
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

# @app.post("/api/auth/reset-password", response_model=MessageResponse)
# async def reset_password(request: ResetPasswordRequest):
#     """Reset password using token"""
#     try:
#         auth_service.reset_password(request.token, request.new_password)
#         return MessageResponse(message="Password reset successful")
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

# # ==================== ANALYSIS ENDPOINTS ====================

# class AnalysisResponse(BaseModel):
#     score: int
#     score_explanation: str
#     summary: str
#     improvements: str
#     job_roles: str
#     ats_score: int
#     keyword_score: int
#     format_score: int
#     header_score: int
#     readability_score: int

# def parse_analysis(response_text: str) -> dict:
#     """Parse the Gemini response into structured data"""
#     match = re.search(r'(?:score|rating)\s*[:\-]?\s*(\d{1,3})', response_text, re.IGNORECASE)
#     score = max(0, min(int(match.group(1)), 100)) if match else 0
    
#     sections = {'score_explanation': '', 'summary': '', 'improvements': '', 'job_roles': ''}
    
#     score_patterns = [r'(?:score|rating|match).*?explanation', r'score analysis', r'match score']
#     summary_patterns = [r'(?:resume )?summary', r'candidate profile', r'overview', r'professional summary']
#     improvement_patterns = [r'improvements?', r'recommendations?', r'suggestions?', r'areas? (?:to|for) improve', r'how to improve']
#     job_role_patterns = [r'suitable.*?(?:job|role|position)s?', r'job.*?roles?', r'recommended.*?(?:job|role|position)s?', r'career.*?(?:path|option|suggestion)s?']
    
#     text_lower = response_text.lower()
    
#     for pattern in score_patterns:
#         match = re.search(pattern, text_lower)
#         if match:
#             start = match.end()
#             next_section = re.search(r'(?:summary|improvements?|recommendations?)', text_lower[start:])
#             end = start + next_section.start() if next_section else start + 500
#             sections['score_explanation'] = response_text[start:end].strip(' :\n-*#')
#             break
    
#     for pattern in summary_patterns:
#         match = re.search(pattern, text_lower)
#         if match:
#             start = match.end()
#             next_section = re.search(r'(?:improvements?|recommendations?|suggestions?)', text_lower[start:])
#             end = start + next_section.start() if next_section else start + 800
#             sections['summary'] = response_text[start:end].strip(' :\n-*#')
#             break
    
#     for pattern in improvement_patterns:
#         match = re.search(pattern, text_lower)
#         if match:
#             start = match.end()
#             next_section = re.search(r'(?:suitable|job roles?|recommended roles?|career)', text_lower[start:])
#             end = start + next_section.start() if next_section else len(response_text)
#             sections['improvements'] = response_text[start:end].strip(' :\n-*#')
#             break
    
#     for pattern in job_role_patterns:
#         match = re.search(pattern, text_lower)
#         if match:
#             start = match.end()
#             sections['job_roles'] = response_text[start:].strip(' :\n-*#')
#             break
    
#     if not any(sections.values()):
#         parts = re.split(r'\n(?=\d\.|\*\*)', response_text)
#         if len(parts) >= 4:
#             sections['score_explanation'] = parts[0]
#             sections['summary'] = parts[1] if len(parts) > 1 else ""
#             sections['improvements'] = '\n'.join(parts[2:4]) if len(parts) > 2 else ""
#             sections['job_roles'] = '\n'.join(parts[4:]) if len(parts) > 4 else ""
#         else:
#             paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
#             if len(paragraphs) >= 4:
#                 sections['score_explanation'] = paragraphs[0]
#                 sections['summary'] = paragraphs[1]
#                 sections['improvements'] = '\n\n'.join(paragraphs[2:4])
#                 sections['job_roles'] = '\n\n'.join(paragraphs[4:]) if len(paragraphs) > 4 else "Based on your skills, consider roles in software engineering, data science, or related technical fields."
#             else:
#                 sections['score_explanation'] = "Resume analyzed against job requirements"
#                 sections['summary'] = response_text[:500] if len(response_text) > 500 else response_text
#                 sections['improvements'] = "Consider tailoring your resume to highlight relevant skills mentioned in the job description"
#                 sections['job_roles'] = "Software Engineer, Data Analyst, Technical Consultant"
    
#     ats_scores = {'ats_score': 0, 'keyword_score': 0, 'format_score': 0, 'header_score': 0, 'readability_score': 0}
    
#     ats_patterns = [
#         (r'ats\s*(?:score|compatibility)?\s*[:\-]?\s*(\d{1,3})', 'ats_score'),
#         (r'keyword\s*(?:score|match)?\s*[:\-]?\s*(\d{1,3})', 'keyword_score'),
#         (r'format(?:ting)?\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'format_score'),
#         (r'(?:section\s*)?header\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'header_score'),
#         (r'readability\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'readability_score'),
#     ]
    
#     for pattern, key in ats_patterns:
#         match = re.search(pattern, response_text, re.IGNORECASE)
#         if match:
#             val = int(match.group(1))
#             ats_scores[key] = max(0, min(val, 100))
    
#     if ats_scores['ats_score'] == 0:
#         ats_scores['ats_score'] = score
#     if ats_scores['keyword_score'] == 0:
#         ats_scores['keyword_score'] = score
#     if ats_scores['format_score'] == 0:
#         ats_scores['format_score'] = score
#     if ats_scores['header_score'] == 0:
#         ats_scores['header_score'] = score
#     if ats_scores['readability_score'] == 0:
#         ats_scores['readability_score'] = score
    
#     return {
#         'score': score,
#         'score_explanation': sections['score_explanation'][:600] if sections['score_explanation'] else "Resume evaluated based on job requirements",
#         'summary': sections['summary'][:1200] if sections['summary'] else "Professional background and qualifications reviewed",
#         'improvements': sections['improvements'][:3000] if sections['improvements'] else "Focus on highlighting relevant experience and skills that match the job description",
#         'job_roles': sections['job_roles'][:1500] if sections['job_roles'] else "Consider roles aligned with your technical expertise and experience",
#         'ats_score': ats_scores['ats_score'],
#         'keyword_score': ats_scores['keyword_score'],
#         'format_score': ats_scores['format_score'],
#         'header_score': ats_scores['header_score'],
#         'readability_score': ats_scores['readability_score']
#     }

# @app.post("/analyze", response_model=AnalysisResponse)
# async def analyze_resume(
#     resume: UploadFile = File(...),
#     job_description: str = Form(...),
#     current_user: dict = Depends(get_current_user)
# ):
#     """Analyze resume against job description (Protected)"""
    
#     if not GEMINI_API_KEY:
#         raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
#     pdf_content = await resume.read()
    
#     if not resume.filename.lower().endswith('.pdf'): # type: ignore
#         raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
#     prompt = f"""Analyze this resume PDF against the provided job description and provide a detailed evaluation.

# JOB DESCRIPTION:
# {job_description}

# Please provide your analysis in the following format:

# SCORE: [Provide a numerical score from 0-100 indicating how well the resume matches the job requirements]

# SCORE EXPLANATION: [Provide 2-3 sentences explaining why you gave this score, mentioning key matching and missing elements]

# ATS SCORES: [Provide these specific ATS compatibility metrics, each as a number from 0-100]
# - ATS SCORE: [Overall ATS compatibility score]
# - KEYWORD SCORE: [How well the resume keywords match the job description]
# - FORMAT SCORE: [How ATS-friendly the resume formatting is]
# - HEADER SCORE: [How well standard section headers are used]
# - READABILITY SCORE: [How easy the resume is to parse]

# SUMMARY: [Provide a 3-4 sentence professional summary of the candidate's background, key skills, and experience level]

# IMPROVEMENTS: [Provide 7-10 specific, actionable bullet points on how to improve this resume for this particular job. Be comprehensive and detailed.]

# SUITABLE JOB ROLES: [Based on the candidate's skills and experience, suggest 5-8 job roles/titles that would be a good fit.]

# Make your analysis specific, actionable, and comprehensive."""

#     try:
#         response = client.models.generate_content(
#             model='gemini-2.5-flash-lite',
#             contents=[
#                 types.Part.from_bytes(data=pdf_content, mime_type='application/pdf'),
#                 prompt
#             ]
#         )
        
#         response_text = response.text
#         analysis = parse_analysis(response_text) # type: ignore
        
#         # Save to database
#         with get_db_cursor() as cursor:
#             cursor.execute(
#                 """
#                 INSERT INTO resume_analyses (user_id, filename, score, ats_score)
#                 VALUES (%s, %s, %s, %s)
#                 """,
#                 (current_user['id'], resume.filename, analysis['score'], analysis['ats_score'])
#             )
        
#         return AnalysisResponse(**analysis)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

# class ChatResponse(BaseModel):
#     response: str

# @app.post("/chat", response_model=ChatResponse)
# async def chat_with_ai(
#     resume: UploadFile = File(None),
#     message: str = Form(...),
#     options: str = Form(""),
#     current_user: dict = Depends(get_optional_user)
# ):
#     """Chat endpoint for conversational AI responses (Optional auth)"""
    
#     if not GEMINI_API_KEY:
#         raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
#     option_list = [o.strip() for o in options.split(',') if o.strip()]
    
#     context_parts = []
#     if 'general' in option_list:
#         context_parts.append("- Provide general resume feedback")
#     if 'ats' in option_list:
#         context_parts.append("- Check ATS (Applicant Tracking System) compatibility")
#     if 'keywords' in option_list:
#         context_parts.append("- Analyze keyword usage and suggest improvements")
#     if 'formatting' in option_list:
#         context_parts.append("- Review formatting and layout")
#     if 'skills' in option_list:
#         context_parts.append("- Identify skills gaps")
#     if 'experience' in option_list:
#         context_parts.append("- Analyze experience section")
    
#     options_context = '\n'.join(context_parts) if context_parts else "- General resume assistance"
    
#     prompt = f"""You are a helpful AI resume assistant having a conversation with a user.

# User's message: {message}

# Focus areas (if resume provided):
# {options_context}

# Instructions:
# - Respond in a friendly, conversational tone
# - Keep responses concise but helpful
# - Use simple dashes (-) for bullet points, NEVER use asterisks (*)
# - Don't use markdown headers, bold text (**), or any markdown formatting
# - If no resume is provided, still help with general resume advice based on the user's question
# - If analyzing a resume for ATS compatibility, ALWAYS start your response with "ATS Score: X/100" where X is your estimated ATS compatibility score, then explain your reasoning
# - Format the ATS score on its own line at the very beginning"""

#     try:
#         contents = []
        
#         if resume and resume.filename:
#             pdf_content = await resume.read()
#             contents.append(types.Part.from_bytes(data=pdf_content, mime_type='application/pdf'))
        
#         contents.append(prompt)
        
#         response = client.models.generate_content(
#             model='gemini-2.5-flash-lite',
#             contents=contents
#         )
        
#         clean_response = response.text.replace('*', '')
        
#         return ChatResponse(response=clean_response)
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# # ==================== PAGE ROUTES ====================

# @app.get("/")
# @app.get("/dashboard")
# async def dashboard():
#     return FileResponse(str(FRONTEND_DIR / "dashboard.html"))

# @app.get("/analysis")
# async def analysis_page():
#     return FileResponse(str(FRONTEND_DIR / "analysis.html"))

# @app.get("/chat")
# async def chat_page():
#     return FileResponse(str(FRONTEND_DIR / "chat.html"))

# @app.get("/login")
# async def login_page():
#     return FileResponse(str(FRONTEND_DIR / "login.html"))

# @app.get("/signup")
# async def signup_page():
#     return FileResponse(str(FRONTEND_DIR / "signup.html"))

# @app.get("/health")
# async def health_check():
#     """Check if API key is configured"""
#     return {
#         "status": "healthy",
#         "gemini_configured": bool(GEMINI_API_KEY)
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import re
from dotenv import load_dotenv
from pathlib import Path

# Import auth modules
from backend.auth_models import (
    SignupRequest, LoginRequest, GoogleSignInRequest, ForgotPasswordRequest, 
    ResetPasswordRequest, LoginResponse, MessageResponse, UserResponse
)
from backend.auth_service import auth_service
from backend.auth_middleware import get_current_user, get_optional_user
from backend.google_auth import google_auth_service
from backend.database import get_db_cursor

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI()

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set")
else:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"✅ Gemini API configured successfully")

# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/signup", response_model=UserResponse)
async def signup(request: SignupRequest):
    """Create new user account"""
    try:
        user = auth_service.signup(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        return UserResponse(
            id=user['id'],
            email=user['email'],
            full_name=user.get('full_name')
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and create session"""
    try:
        result = auth_service.login(
            email=request.email,
            password=request.password
        )
        return LoginResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/auth/google", response_model=LoginResponse)
async def google_signin(request: GoogleSignInRequest):
    """Sign in with Google"""
    try:
        result = google_auth_service.google_signin(request.token)
        return LoginResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google sign-in failed: {str(e)}")

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user"""
    return UserResponse(**current_user)

@app.post("/api/auth/logout", response_model=MessageResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout and invalidate session"""
    # Extract token from request (handled in dependency)
    return MessageResponse(message="Logged out successfully")

@app.post("/api/auth/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """Request password reset token"""
    try:
        result = auth_service.request_password_reset(request.email)
        # In production, send email with token
        # For development, return token in response
        return MessageResponse(
            message=f"Password reset token generated. Token: {result['token']} (In production, this would be emailed)"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

@app.post("/api/auth/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """Reset password using token"""
    try:
        auth_service.reset_password(request.token, request.new_password)
        return MessageResponse(message="Password reset successful")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

# ==================== ANALYSIS ENDPOINTS ====================

class AnalysisResponse(BaseModel):
    score: int
    score_explanation: str
    summary: str
    improvements: str
    job_roles: str
    ats_score: int
    keyword_score: int
    format_score: int
    header_score: int
    readability_score: int

def parse_analysis(response_text: str) -> dict:
    """Parse the Gemini response into structured data"""
    match = re.search(r'(?:score|rating)\s*[:\-]?\s*(\d{1,3})', response_text, re.IGNORECASE)
    score = max(0, min(int(match.group(1)), 100)) if match else 0
    
    sections = {'score_explanation': '', 'summary': '', 'improvements': '', 'job_roles': ''}
    
    score_patterns = [r'(?:score|rating|match).*?explanation', r'score analysis', r'match score']
    summary_patterns = [r'(?:resume )?summary', r'candidate profile', r'overview', r'professional summary']
    improvement_patterns = [r'improvements?', r'recommendations?', r'suggestions?', r'areas? (?:to|for) improve', r'how to improve']
    job_role_patterns = [r'suitable.*?(?:job|role|position)s?', r'job.*?roles?', r'recommended.*?(?:job|role|position)s?', r'career.*?(?:path|option|suggestion)s?']
    
    text_lower = response_text.lower()
    
    for pattern in score_patterns:
        match = re.search(pattern, text_lower)
        if match:
            start = match.end()
            next_section = re.search(r'(?:summary|improvements?|recommendations?)', text_lower[start:])
            end = start + next_section.start() if next_section else start + 500
            sections['score_explanation'] = response_text[start:end].strip(' :\n-*#')
            break
    
    for pattern in summary_patterns:
        match = re.search(pattern, text_lower)
        if match:
            start = match.end()
            next_section = re.search(r'(?:improvements?|recommendations?|suggestions?)', text_lower[start:])
            end = start + next_section.start() if next_section else start + 800
            sections['summary'] = response_text[start:end].strip(' :\n-*#')
            break
    
    for pattern in improvement_patterns:
        match = re.search(pattern, text_lower)
        if match:
            start = match.end()
            next_section = re.search(r'(?:suitable|job roles?|recommended roles?|career)', text_lower[start:])
            end = start + next_section.start() if next_section else len(response_text)
            sections['improvements'] = response_text[start:end].strip(' :\n-*#')
            break
    
    for pattern in job_role_patterns:
        match = re.search(pattern, text_lower)
        if match:
            start = match.end()
            sections['job_roles'] = response_text[start:].strip(' :\n-*#')
            break
    
    if not any(sections.values()):
        parts = re.split(r'\n(?=\d\.|\*\*)', response_text)
        if len(parts) >= 4:
            sections['score_explanation'] = parts[0]
            sections['summary'] = parts[1] if len(parts) > 1 else ""
            sections['improvements'] = '\n'.join(parts[2:4]) if len(parts) > 2 else ""
            sections['job_roles'] = '\n'.join(parts[4:]) if len(parts) > 4 else ""
        else:
            paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
            if len(paragraphs) >= 4:
                sections['score_explanation'] = paragraphs[0]
                sections['summary'] = paragraphs[1]
                sections['improvements'] = '\n\n'.join(paragraphs[2:4])
                sections['job_roles'] = '\n\n'.join(paragraphs[4:]) if len(paragraphs) > 4 else "Based on your skills, consider roles in software engineering, data science, or related technical fields."
            else:
                sections['score_explanation'] = "Resume analyzed against job requirements"
                sections['summary'] = response_text[:500] if len(response_text) > 500 else response_text
                sections['improvements'] = "Consider tailoring your resume to highlight relevant skills mentioned in the job description"
                sections['job_roles'] = "Software Engineer, Data Analyst, Technical Consultant"
    
    ats_scores = {'ats_score': 0, 'keyword_score': 0, 'format_score': 0, 'header_score': 0, 'readability_score': 0}
    
    ats_patterns = [
        (r'ats\s*(?:score|compatibility)?\s*[:\-]?\s*(\d{1,3})', 'ats_score'),
        (r'keyword\s*(?:score|match)?\s*[:\-]?\s*(\d{1,3})', 'keyword_score'),
        (r'format(?:ting)?\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'format_score'),
        (r'(?:section\s*)?header\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'header_score'),
        (r'readability\s*(?:score)?\s*[:\-]?\s*(\d{1,3})', 'readability_score'),
    ]
    
    for pattern, key in ats_patterns:
        match = re.search(pattern, response_text, re.IGNORECASE)
        if match:
            val = int(match.group(1))
            ats_scores[key] = max(0, min(val, 100))
    
    if ats_scores['ats_score'] == 0:
        ats_scores['ats_score'] = score
    if ats_scores['keyword_score'] == 0:
        ats_scores['keyword_score'] = score
    if ats_scores['format_score'] == 0:
        ats_scores['format_score'] = score
    if ats_scores['header_score'] == 0:
        ats_scores['header_score'] = score
    if ats_scores['readability_score'] == 0:
        ats_scores['readability_score'] = score
    
    return {
        'score': score,
        'score_explanation': sections['score_explanation'][:600] if sections['score_explanation'] else "Resume evaluated based on job requirements",
        'summary': sections['summary'][:1200] if sections['summary'] else "Professional background and qualifications reviewed",
        'improvements': sections['improvements'][:3000] if sections['improvements'] else "Focus on highlighting relevant experience and skills that match the job description",
        'job_roles': sections['job_roles'][:1500] if sections['job_roles'] else "Consider roles aligned with your technical expertise and experience",
        'ats_score': ats_scores['ats_score'],
        'keyword_score': ats_scores['keyword_score'],
        'format_score': ats_scores['format_score'],
        'header_score': ats_scores['header_score'],
        'readability_score': ats_scores['readability_score']
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Analyze resume against job description (Protected)"""
    
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    pdf_content = await resume.read()
    
    if not resume.filename.lower().endswith('.pdf'): # type: ignore
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    prompt = f"""Analyze this resume PDF against the provided job description and provide a detailed evaluation.

JOB DESCRIPTION:
{job_description}

Please provide your analysis in the following format:

SCORE: [Provide a numerical score from 0-100 indicating how well the resume matches the job requirements]

SCORE EXPLANATION: [Provide 2-3 sentences explaining why you gave this score, mentioning key matching and missing elements]

ATS SCORES: [Provide these specific ATS compatibility metrics, each as a number from 0-100]
- ATS SCORE: [Overall ATS compatibility score]
- KEYWORD SCORE: [How well the resume keywords match the job description]
- FORMAT SCORE: [How ATS-friendly the resume formatting is]
- HEADER SCORE: [How well standard section headers are used]
- READABILITY SCORE: [How easy the resume is to parse]

SUMMARY: [Provide a 3-4 sentence professional summary of the candidate's background, key skills, and experience level]

IMPROVEMENTS: [Provide 7-10 specific, actionable bullet points on how to improve this resume for this particular job. Be comprehensive and detailed.]

SUITABLE JOB ROLES: [Based on the candidate's skills and experience, suggest 5-8 job roles/titles that would be a good fit.]

Make your analysis specific, actionable, and comprehensive."""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=pdf_content, mime_type='application/pdf'),
                prompt
            ]
        )
        
        response_text = response.text
        analysis = parse_analysis(response_text) # type: ignore
        
        # Save to database
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO resume_analyses (user_id, filename, score, ats_score)
                VALUES (%s, %s, %s, %s)
                """,
                (current_user['id'], resume.filename, analysis['score'], analysis['ats_score'])
            )
        
        return AnalysisResponse(**analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    resume: UploadFile = File(None),
    message: str = Form(...),
    options: str = Form(""),
    current_user: dict = Depends(get_optional_user)
):
    """Chat endpoint for conversational AI responses (Optional auth)"""
    
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    option_list = [o.strip() for o in options.split(',') if o.strip()]
    
    context_parts = []
    if 'general' in option_list:
        context_parts.append("- Provide general resume feedback")
    if 'ats' in option_list:
        context_parts.append("- Check ATS (Applicant Tracking System) compatibility")
    if 'keywords' in option_list:
        context_parts.append("- Analyze keyword usage and suggest improvements")
    if 'formatting' in option_list:
        context_parts.append("- Review formatting and layout")
    if 'skills' in option_list:
        context_parts.append("- Identify skills gaps")
    if 'experience' in option_list:
        context_parts.append("- Analyze experience section")
    
    options_context = '\n'.join(context_parts) if context_parts else "- General resume assistance"
    
    prompt = f"""You are a professional AI resume analyst. Analyze the resume and provide structured feedback.

User's message: {message}

Analysis areas requested:
{options_context}

FORMATTING INSTRUCTIONS (FOLLOW EXACTLY):
1. If ATS analysis is requested, start with: "ATS Score: X/100" on its own line
2. Use clear section headers followed by a colon, like:
   - Skills Gap Analysis:
   - ATS Compatibility:
   - Keyword Analysis:
   - Formatting Review:
   - Experience Analysis:
   - Recommendations:
3. Use bullet points with dashes (-) for lists
4. Be specific and actionable
5. DO NOT use asterisks (*), markdown, or any special formatting
6. Keep each section concise but informative

Example structure:
ATS Score: 75/100

Skills Gap Analysis:
- Missing skill 1 that is commonly required
- Missing skill 2 for this role

Recommendations:
- Add specific keywords like X, Y, Z
- Improve section formatting

Provide your analysis now:"""

    try:
        contents = []
        
        if resume and resume.filename:
            pdf_content = await resume.read()
            contents.append(types.Part.from_bytes(data=pdf_content, mime_type='application/pdf'))
        
        contents.append(prompt)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents
        )
        
        clean_response = response.text.replace('*', '')
        
        return ChatResponse(response=clean_response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# ==================== PAGE ROUTES ====================

@app.get("/")
@app.get("/dashboard")
async def dashboard():
    return FileResponse(str(FRONTEND_DIR / "dashboard.html"))

@app.get("/analysis")
async def analysis_page():
    return FileResponse(str(FRONTEND_DIR / "analysis.html"))

@app.get("/chat")
async def chat_page():
    return FileResponse(str(FRONTEND_DIR / "chat.html"))

@app.get("/profile")
async def profile_page():
    return FileResponse(str(FRONTEND_DIR / "profile.html"))

@app.get("/api/config/auth")
async def auth_config():
    import os
    return {"googleClientId": os.getenv("GOOGLE_CLIENT_ID")}

@app.get("/login")
async def login_page():
    return FileResponse(str(FRONTEND_DIR / "login.html"))

@app.get("/signup")
async def signup_page():
    return FileResponse(str(FRONTEND_DIR / "signup.html"))

@app.get("/forgot-password")
async def forgot_password_page():
    return FileResponse(str(FRONTEND_DIR / "forgot-password.html"))

@app.get("/reset-password")
async def reset_password_page():
    return FileResponse(str(FRONTEND_DIR / "reset-password.html"))

@app.get("/jobs")
async def jobs_page():
    return FileResponse(str(FRONTEND_DIR / "jobs.html"))

# ==================== JOB MATCHING API ====================

@app.post("/api/find-jobs")
async def find_jobs(resume: UploadFile = File(None), query: str = Form("")):
    """Find matching jobs based on resume and/or query"""
    from backend.job_matcher import job_matcher
    
    try:
        resume_text = ""
        
        # Extract text from resume if provided
        if resume and resume.filename:
            pdf_content = await resume.read()
            
            extract_prompt = "Extract all text content from this resume PDF. Return only the plain text, no formatting."
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=pdf_content, mime_type='application/pdf'),
                    extract_prompt
                ]
            )
            
            resume_text = response.text
        
        # Append user query to provide additional context
        if query.strip():
            resume_text += f"\n\nUser job preferences: {query}"
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Please provide a resume or job preferences")
        
        # Find matching jobs
        result = await job_matcher.find_matching_jobs(resume_text)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check if API key is configured"""
    return {
        "status": "healthy",
        "gemini_configured": bool(GEMINI_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

