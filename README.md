# Resume Analyzer & Job Matcher

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2?style=flat-square&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A production-grade full-stack application leveraging Google's Gemini 2.5 Flash multimodal AI for intelligent resume analysis, ATS compatibility scoring, and automated job matching across multiple employment platforms.

[Overview](#overview) · [Architecture](#system-architecture) · [Installation](#installation) · [API Documentation](#api-reference) · [Deployment](#deployment)

</div>

---

## Overview

This application provides an end-to-end solution for job seekers and recruiters, combining advanced AI capabilities with practical career tools:

- **Intelligent Resume Analysis**: Multimodal AI parsing of PDF resumes with structured feedback
- **ATS Compatibility Scoring**: Five-metric evaluation system for applicant tracking system optimization  
- **Conversational AI Assistant**: Context-aware chat interface for personalized resume improvement
- **Automated Job Matching**: Real-time aggregation from Adzuna, JSearch, and ArbeitNow APIs
- **Secure Authentication**: Dual-provider auth (Email + Google OAuth 2.0) with session management

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [Authentication Flow](#authentication-flow)
5. [AI Pipeline](#ai-pipeline)
6. [Job Matching Engine](#job-matching-engine)
7. [Installation](#installation)
8. [API Reference](#api-reference)
9. [Project Structure](#project-structure)
10. [Security Implementation](#security-implementation)
11. [Deployment](#deployment)
12. [Technical Highlights](#technical-highlights)

---

## System Architecture

The application follows a layered architecture pattern with clear separation of concerns:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                               PRESENTATION LAYER                              │
│                                                                               │
│   Dashboard    │    Analysis    │    Chat    │    Jobs    │    Auth Pages    │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                                API GATEWAY                                    │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  CORS Middleware  │  Auth Middleware  │  Request Validation (Pydantic)  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│  Route Handlers:  /analyze  │  /chat  │  /api/auth/*  │  /api/find-jobs     │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                               SERVICE LAYER                                   │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │   AuthService    │  │  GoogleAuthSvc   │  │      JobMatcher          │   │
│  │                  │  │                  │  │                          │   │
│  │  • signup()      │  │  • verify_token  │  │  • extract_resume_data() │   │
│  │  • login()       │  │  • google_signin │  │  • fetch_all_jobs()      │   │
│  │  • verify_sess() │  │  • create_user   │  │  • calculate_match()     │   │
│  │  • reset_pass()  │  │                  │  │  • rank_jobs()           │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘   │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             INFRASTRUCTURE LAYER                              │
│                                                                               │
│  ┌────────────────────┐    ┌─────────────────────────────────────────────┐   │
│  │     PostgreSQL     │    │           External APIs                     │   │
│  │                    │    │                                             │   │
│  │  • Neon (Cloud)    │    │   Gemini 2.5   │   Adzuna   │   JSearch    │   │
│  │  • Docker (Local)  │    │                                             │   │
│  └────────────────────┘    └─────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Separation of Concerns** | Distinct layers for routing, business logic, and data access |
| **Dependency Injection** | FastAPI's `Depends()` for middleware and service injection |
| **Single Responsibility** | Each service handles one domain (auth, jobs, analysis) |
| **Fail-Fast Validation** | Pydantic models validate all inputs at API boundary |

---

## Technology Stack

### Core Framework

| Component | Technology | Justification |
|-----------|------------|---------------|
| Web Framework | FastAPI 0.104+ | Async-first design, automatic OpenAPI generation, native Pydantic integration |
| Runtime | Python 3.9+ | Type hints, async/await support, extensive library ecosystem |
| ASGI Server | Uvicorn | Production-ready async server with hot reload for development |
| Validation | Pydantic v2 | Runtime type checking, serialization, EmailStr validation |

### Data Layer

| Component | Technology | Justification |
|-----------|------------|---------------|
| Primary Database | PostgreSQL 15 | ACID compliance, robust indexing, JSON support |
| Cloud Database | Neon | Serverless PostgreSQL, automatic scaling, branch-based development |
| Database Driver | psycopg2-binary | Industry standard, connection pooling, RealDictCursor support |
| Local Development | Docker Compose | Reproducible environments, volume persistence |

### AI & External Services

| Component | Technology | Justification |
|-----------|------------|---------------|
| AI Model | Gemini 2.5 Flash | Multimodal (native PDF), fast inference, latest architecture |
| AI SDK | google-genai | Official SDK with type safety and async support |
| Job API 1 | Adzuna (RapidAPI) | Global coverage, salary data, 10M+ listings |
| Job API 2 | JSearch (OpenWebNinja) | Real-time data, company information |
| Job API 3 | ArbeitNow | Free tier, European coverage, remote-focused |

### Security

| Component | Technology | Justification |
|-----------|------------|---------------|
| Password Hashing | Argon2id | PHC winner, memory-hard, GPU/ASIC resistant |
| OAuth Provider | Google OAuth 2.0 | Trusted IdP, verified email, profile data |
| Session Tokens | secrets.token_urlsafe | 256-bit cryptographic entropy |
| Email Validation | dnspython | MX record verification, disposable domain blocking |

---

## Database Schema

### Entity Relationship Model

```
┌────────────────────────────────────────────────────────────────────────────┐
│                            USERS                                            │
├────────────────────────────────────────────────────────────────────────────┤
│  id              SERIAL PRIMARY KEY                                         │
│  email           VARCHAR(255) UNIQUE NOT NULL                               │
│  password_hash   VARCHAR(255)                                               │
│  full_name       VARCHAR(255)                                               │
│  google_id       VARCHAR(255) UNIQUE                                        │
│  profile_picture VARCHAR(500)                                               │
│  auth_provider   VARCHAR(50) DEFAULT 'email'                                │
│  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP                        │
│  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP                        │
│  is_active       BOOLEAN DEFAULT TRUE                                       │
│  email_verified  BOOLEAN DEFAULT FALSE                                      │
└────────────────────────────────────────────────────────────────────────────┘
        │
        │ 1:N
        ├──────────────────────────────────────────────────────┐
        │                                                      │
        ▼                                                      ▼
┌─────────────────────────────┐               ┌─────────────────────────────┐
│   PASSWORD_RESET_TOKENS     │               │       USER_SESSIONS         │
├─────────────────────────────┤               ├─────────────────────────────┤
│  id         SERIAL PK       │               │  id            SERIAL PK    │
│  user_id    INTEGER FK      │               │  user_id       INTEGER FK   │
│  token      VARCHAR(255) UQ │               │  session_token VARCHAR UQ   │
│  expires_at TIMESTAMP       │               │  expires_at    TIMESTAMP    │
│  used       BOOLEAN         │               │  created_at    TIMESTAMP    │
│  created_at TIMESTAMP       │               │  last_activity TIMESTAMP    │
└─────────────────────────────┘               └─────────────────────────────┘
        │
        │ 1:N
        ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                         RESUME_ANALYSES                                     │
├────────────────────────────────────────────────────────────────────────────┤
│  id         SERIAL PRIMARY KEY                                              │
│  user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE                 │
│  filename   VARCHAR(255)                                                    │
│  score      INTEGER                                                         │
│  ats_score  INTEGER                                                         │
│  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Index Strategy

```sql
-- Primary lookup patterns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_reset_tokens_token ON password_reset_tokens(token);

-- Relationship traversal
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_analyses_user ON resume_analyses(user_id);

-- Maintenance operations
CREATE INDEX idx_reset_tokens_expires ON password_reset_tokens(expires_at);
```

### Schema Design Rationale

1. **Referential Integrity**: `ON DELETE CASCADE` ensures orphan cleanup
2. **Provider Flexibility**: `auth_provider` field supports multiple authentication methods
3. **Session Management**: Separate sessions table enables multi-device support and granular revocation
4. **Audit Compliance**: Timestamps on all entities for logging and debugging
5. **Soft Delete**: `is_active` flag preserves data while disabling accounts

---

## Authentication Flow

### Email Authentication Sequence

```
┌──────────┐                         ┌──────────┐                         ┌──────────┐
│  Client  │                         │  Server  │                         │ Database │
└────┬─────┘                         └────┬─────┘                         └────┬─────┘
     │                                    │                                    │
     │  POST /api/auth/signup             │                                    │
     │  {email, password, full_name}      │                                    │
     │───────────────────────────────────►│                                    │
     │                                    │                                    │
     │                                    │  Validate email format             │
     │                                    │  Check disposable domains          │
     │                                    │  Verify MX records (DNS)           │
     │                                    │                                    │
     │                                    │  SELECT * FROM users WHERE email   │
     │                                    │───────────────────────────────────►│
     │                                    │◄───────────────────────────────────│
     │                                    │                                    │
     │                                    │  Hash password (Argon2id)          │
     │                                    │                                    │
     │                                    │  INSERT INTO users                 │
     │                                    │───────────────────────────────────►│
     │                                    │◄───────────────────────────────────│
     │                                    │                                    │
     │  Response: {id, email, full_name}  │                                    │
     │◄───────────────────────────────────│                                    │
     │                                    │                                    │
     │  POST /api/auth/login              │                                    │
     │  {email, password}                 │                                    │
     │───────────────────────────────────►│                                    │
     │                                    │                                    │
     │                                    │  Fetch user, verify Argon2 hash    │
     │                                    │  Generate session token            │
     │                                    │  INSERT INTO user_sessions         │
     │                                    │───────────────────────────────────►│
     │                                    │◄───────────────────────────────────│
     │                                    │                                    │
     │  Response: {user, session_token}   │                                    │
     │◄───────────────────────────────────│                                    │
```

### Google OAuth 2.0 Sequence

```
┌──────────┐        ┌──────────┐        ┌──────────┐        ┌──────────┐
│  Client  │        │  Google  │        │  Server  │        │ Database │
└────┬─────┘        └────┬─────┘        └────┬─────┘        └────┬─────┘
     │                   │                   │                   │
     │  Sign-In Click    │                   │                   │
     │──────────────────►│                   │                   │
     │                   │                   │                   │
     │  ID Token         │                   │                   │
     │◄──────────────────│                   │                   │
     │                   │                   │                   │
     │  POST /api/auth/google               │                   │
     │  {token: id_token}                   │                   │
     │─────────────────────────────────────►│                   │
     │                   │                   │                   │
     │                   │  Verify Token     │                   │
     │                   │◄──────────────────│                   │
     │                   │──────────────────►│                   │
     │                   │                   │                   │
     │                   │                   │  Upsert user      │
     │                   │                   │──────────────────►│
     │                   │                   │◄──────────────────│
     │                   │                   │                   │
     │                   │                   │  Create session   │
     │                   │                   │──────────────────►│
     │                   │                   │◄──────────────────│
     │                   │                   │                   │
     │  Response: {user, session_token}     │                   │
     │◄─────────────────────────────────────│                   │
```

### Password Hashing Configuration

```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=2,          # Iterations
    memory_cost=65536,    # 64 MB memory
    parallelism=4,        # Parallel threads
    hash_len=32,          # Hash length
    salt_len=16           # Salt length
)
```

**Argon2id Selection Criteria:**
- Winner of the 2015 Password Hashing Competition
- Memory-hard algorithm resistant to GPU/ASIC attacks
- Configurable parameters for future security requirements
- Automatic salt generation and secure comparison

---

## AI Pipeline

### Resume Analysis Workflow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         RESUME ANALYSIS PIPELINE                            │
└────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │   PDF Upload    │
    │  (multipart)    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  File Type      │────── Invalid ──────► HTTP 400 Bad Request
    │  Validation     │
    └────────┬────────┘
             │ Valid PDF
             ▼
    ┌─────────────────┐     ┌────────────────────────────────────────────┐
    │   Gemini 2.5    │     │              PROMPT TEMPLATE                │
    │   Flash API     │◄────┤                                            │
    │                 │     │  • Job description context injection       │
    │   (Multimodal)  │     │  • Structured output specification         │
    │                 │     │  • ATS-specific evaluation criteria        │
    └────────┬────────┘     └────────────────────────────────────────────┘
             │
             ▼
    ┌─────────────────┐
    │    Response     │     Extracted Fields:
    │    Parser       │───► • Overall Match Score (0-100)
    │   (Regex-based) │     • ATS Compatibility (5 metrics)
    └────────┬────────┘     • Summary, Improvements, Roles
             │
             ▼
    ┌─────────────────┐
    │   Persistence   │────► resume_analyses table
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  JSON Response  │
    │                 │
    │  AnalysisResponse {
    │    score: int
    │    ats_score: int
    │    keyword_score: int
    │    format_score: int
    │    header_score: int
    │    readability_score: int
    │    summary: str
    │    improvements: str
    │    job_roles: str
    │  }
    └─────────────────┘
```

### Multimodal Processing

```python
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[
        types.Part.from_bytes(data=pdf_content, mime_type='application/pdf'),
        prompt
    ]
)
```

**Technical Advantages:**
- Native PDF understanding without OCR preprocessing
- Layout and formatting context preserved
- Single API call for document + text processing
- Optimized Flash model for low-latency inference

---

## Job Matching Engine

### Multi-Source Aggregation Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                       JOB MATCHING PIPELINE                                 │
└────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │   Resume/Query Input  │
                    └───────────┬──────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │  AI Data Extraction  │
                    │                      │
                    │  • Skills[]          │
                    │  • Target Roles[]    │
                    │  • Experience Years  │
                    │  • Location Pref     │
                    │  • Seniority Level   │
                    └───────────┬──────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│    Adzuna     │       │    JSearch    │       │   ArbeitNow   │
│   (RapidAPI)  │       │ (OpenWebNinja)│       │    (Free)     │
│               │       │               │       │               │
│  US/Global    │       │    Global     │       │   EU/Remote   │
│  Salary Data  │       │   Real-time   │       │  No API Key   │
└───────┬───────┘       └───────┬───────┘       └───────┬───────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   asyncio.gather()    │
                    │   (Parallel Fetch)    │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Match Score Calc    │
                    │                       │
                    │   Title:    30 pts    │
                    │   Skills:   50 pts    │
                    │   Remote:   10 pts    │
                    │   Salary:   10 pts    │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │    Ranked Results     │
                    │      (Top 50)         │
                    └───────────────────────┘
```

### Scoring Algorithm

```python
def calculate_match_score(job: Dict, resume_data: Dict) -> float:
    score = 0.0
    
    # Title relevance (30 points)
    for role in resume_data['roles']:
        if any(word in job['title'].lower() for word in role.split()):
            score += 30
            break
    
    # Skills alignment (50 points max, 7 per skill)
    matched = sum(1 for s in resume_data['skills'] if s.lower() in job_text)
    score += min(matched * 7, 50)
    
    # Remote work preference (10 points)
    if job.get('remote'):
        score += 10
    
    # Salary transparency (10 points)
    if job.get('salary', 0) > 0:
        score += 10
    
    return min(score, 100)
```

---

## Installation

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.9+ | Runtime environment |
| Docker | Latest | Local PostgreSQL (optional) |
| Neon Account | - | Cloud PostgreSQL (alternative) |
| Google Cloud | - | Gemini API + OAuth credentials |

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Required: AI Configuration
GEMINI_API_KEY=your_gemini_api_key

# Database: Option A - Neon (Recommended for Production)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Database: Option B - Local Docker
DB_HOST=127.0.0.1
DB_PORT=5555
DB_USER=resumeuser
DB_PASSWORD=resumepass123
DB_NAME=resumedb

# Optional: Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id

# Optional: Job APIs
ADZUNA_RAPIDAPI_KEY=your_adzuna_key
OPENWEBNINJA_API_KEY=your_openwebninja_key

# Session Configuration
SESSION_EXPIRY_HOURS=24
```

### Setup Instructions

```bash
# Clone repository
git clone <repository-url>
cd resume-parser

# Install dependencies
pip install -r requirements.txt

# Database Setup (choose one):

# Option A: Docker (Local Development)
docker-compose up -d

# Option B: Neon (Cloud)
# Set DATABASE_URL in .env, then run:
python setup_neon.py

# Start Application
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Verification

```bash
# Database connection test
python -c "from backend.database import *; print('Database connection successful')"

# Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", "gemini_configured": true}
```

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/api/auth/signup` | Create user account | None |
| `POST` | `/api/auth/login` | Authenticate user | None |
| `POST` | `/api/auth/google` | Google OAuth sign-in | None |
| `GET` | `/api/auth/me` | Get current user | Bearer Token |
| `POST` | `/api/auth/logout` | Invalidate session | Bearer Token |
| `POST` | `/api/auth/forgot-password` | Request reset token | None |
| `POST` | `/api/auth/reset-password` | Reset password | None |

### Analysis Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/analyze` | Analyze resume vs job description | Bearer Token |
| `POST` | `/chat` | AI chat for resume feedback | Optional |
| `POST` | `/api/find-jobs` | Find matching job listings | None |
| `GET` | `/health` | Service health check | None |

### Request/Response Specifications

<details>
<summary><strong>POST /api/auth/signup</strong></summary>

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "minimum8characters",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid email format, disposable email, or user exists
- `500 Internal Server Error`: Database error
</details>

<details>
<summary><strong>POST /api/auth/login</strong></summary>

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userpassword"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "session_token": "abc123...",
  "expires_at": "2026-01-22T12:00:00"
}
```
</details>

<details>
<summary><strong>POST /analyze</strong></summary>

**Request (multipart/form-data):**
- `resume`: PDF file (required)
- `job_description`: string (required)

**Headers:**
```
Authorization: Bearer <session_token>
```

**Response (200 OK):**
```json
{
  "score": 78,
  "score_explanation": "Strong technical background...",
  "summary": "Experienced software engineer...",
  "improvements": "1. Add quantifiable achievements...",
  "job_roles": "Senior Software Engineer, Tech Lead...",
  "ats_score": 82,
  "keyword_score": 75,
  "format_score": 85,
  "header_score": 90,
  "readability_score": 80
}
```
</details>

<details>
<summary><strong>POST /api/find-jobs</strong></summary>

**Request (multipart/form-data):**
- `resume`: PDF file (optional)
- `query`: string - job preferences (optional)

**Response (200 OK):**
```json
{
  "success": true,
  "resume_data": {
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "roles": ["Backend Engineer"],
    "experience_years": 3,
    "location": "Remote"
  },
  "total_jobs": 42,
  "jobs": [
    {
      "source": "Adzuna",
      "title": "Senior Backend Engineer",
      "company": "Tech Corp",
      "location": "Remote",
      "match_score": 87,
      "salary": 150000,
      "url": "https://..."
    }
  ]
}
```
</details>

---

## Project Structure

```
resume-parser/
│
├── backend/
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # FastAPI application, route handlers
│   ├── database.py                 # PostgreSQL connection management
│   ├── auth_service.py             # Authentication business logic
│   ├── auth_middleware.py          # Bearer token middleware
│   ├── auth_models.py              # Pydantic request/response schemas
│   ├── google_auth.py              # Google OAuth 2.0 integration
│   ├── email_validator.py          # Email validation (format, DNS, blocklist)
│   └── job_matcher.py              # Multi-API job aggregation
│
├── frontend/
│   ├── dashboard.html              # Main dashboard
│   ├── analysis.html               # Resume analysis interface
│   ├── chat.html                   # AI chat interface
│   ├── jobs.html                   # Job matching results
│   ├── login.html                  # Authentication page
│   ├── signup.html                 # Registration page
│   ├── profile.html                # User profile
│   ├── forgot-password.html        # Password recovery
│   └── reset-password.html         # Password reset
│
├── docker-compose.yml              # PostgreSQL container configuration
├── init.sql                        # Database schema DDL
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment configuration
├── setup_neon.py                   # Neon database initialization
├── test_db.py                      # Database connection tests
└── README.md                       # Documentation
```

---

## Security Implementation

### Defense Layers

| Layer | Implementation | Protection Against |
|-------|----------------|-------------------|
| Password Storage | Argon2id hashing | Rainbow tables, brute force |
| Session Tokens | `secrets.token_urlsafe(32)` | Prediction, session hijacking |
| Email Validation | Format + MX DNS lookup | Fake/disposable accounts |
| Input Validation | Pydantic models | Injection, malformed data |
| API Authentication | Bearer tokens | Unauthorized access |
| CORS | Configurable origins | Cross-site requests |
| Database Queries | Parameterized statements | SQL injection |

### Disposable Email Prevention

The application blocks registration from 50+ known disposable email providers:

```python
DISPOSABLE_EMAIL_DOMAINS = {
    'tempmail.com', 'guerrillamail.com', 'mailinator.com',
    '10minutemail.com', 'throwaway.email', 'yopmail.com',
    'fakeinbox.com', 'trashmail.com', 'getnada.com',
    # ... additional domains
}
```

---

## Deployment

### Vercel (Serverless)

```json
{
  "builds": [
    {"src": "backend/main.py", "use": "@vercel/python"}
  ],
  "routes": [
    {"src": "/(.*)", "dest": "backend/main.py"}
  ]
}
```

### Docker Compose (Self-Hosted)

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: resumeuser
      POSTGRES_PASSWORD: resumepass123
      POSTGRES_DB: resumedb
    ports:
      - "5555:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U resumeuser -d resumedb"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Neon (Serverless PostgreSQL)

Benefits:
- Automatic connection pooling
- Branch-based development workflow
- Auto-scaling compute resources
- SSL encryption by default

---

## Technical Highlights

### Architecture & Design Patterns

| Aspect | Implementation |
|--------|----------------|
| Layered Architecture | Presentation → API Gateway → Service → Data layers |
| Dependency Injection | FastAPI's `Depends()` for middleware and services |
| Context Managers | Safe database connection handling with automatic cleanup |
| Async/Await | Non-blocking I/O throughout the application |

### Security Engineering

| Aspect | Implementation |
|--------|----------------|
| Password Hashing | Argon2id (PHC winner) vs industry-common bcrypt |
| Token Generation | `secrets.token_urlsafe(32)` - 256-bit entropy |
| Email Validation | Three-layer: format → disposable check → DNS MX |
| OAuth Integration | Google ID token verification with issuer validation |

### AI/ML Integration

| Aspect | Implementation |
|--------|----------------|
| Model Selection | Gemini 2.5 Flash for speed + capability balance |
| Multimodal Processing | Native PDF parsing without OCR dependencies |
| Prompt Engineering | Structured output format for reliable parsing |
| Response Handling | Regex-based extraction with graceful fallbacks |

### Performance Optimization

| Aspect | Implementation |
|--------|----------------|
| Parallel API Calls | `asyncio.gather()` for concurrent job fetching |
| Connection Pooling | psycopg2 with context managers |
| Lazy Processing | On-demand PDF analysis |
| Database Indexing | Strategic indexes on high-frequency lookup columns |

### Code Quality

| Aspect | Implementation |
|--------|----------------|
| Type Safety | Python type hints throughout codebase |
| Data Validation | Pydantic v2 models for all API contracts |
| Error Handling | Structured exceptions with appropriate HTTP codes |
| Modularity | Single-responsibility service classes |

---

## Performance Metrics

| Operation | Expected Latency |
|-----------|-----------------|
| Authentication | < 100ms |
| Resume Analysis (Gemini) | 2-5 seconds |
| Job Search (3 APIs parallel) | 3-8 seconds |
| Database Queries (indexed) | < 10ms |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Resume Analyzer & Job Matcher**

Built with FastAPI · PostgreSQL · Google Gemini AI

</div>