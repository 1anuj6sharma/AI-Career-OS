# AI Career Operating System (AI Career OS)

An autonomous, agentic, end-to-end **AI Career Operating System** built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Alembic**, **LangChain**, **LangGraph**, **Google Gemini**, **Groq**, and **Vanilla Modern CSS/JS Frontend**.

---

## 🌟 Core Architecture & Modules (Modules 1–16)

The system consists of 16 integrated production modules:

1. **User Authentication & Authorization System** (`/api/v1/auth`)
2. **User Profile & Skill Intelligence System** (`/api/v1/profile`)
3. **Job Application & Management System** (`/api/v1/jobs`)
4. **AI Career Intelligence & Insights Engine** (`/api/v1/ai`)
5. **Resume Intelligence & ATS Optimization Engine** (`/api/v1/resumes`)
6. **Interview Intelligence & Preparation Engine** (`/api/v1/interviews`)
7. **Career Roadmap & Execution Engine** (`/api/v1/career`)
8. **Learning Hub & Skill Development Engine** (`/api/v1/learning`)
9. **Portfolio & Personal Brand Engineering System** (`/api/v1/brand`)
10. **Job Opportunity Matching & Recommendation Engine** (`/api/v1/opportunities`)
11. **Networking CRM & Recruiter Relationship Engine** (`/api/v1/network`)
12. **Offer Management & Compensation Decision Matrix** (`/api/v1/offers`)
13. **AI Career Performance, Productivity & Continuous Growth Engine** (`/api/v1/career`)
14. **AI Career Opportunity Intelligence & Job Acquisition Engine** (`/api/v1/opportunities`, `/api/v1/applications`)
15. **AI Career OS Master Orchestrator & Autonomous Career Agent** (`/api/v1/master-orchestrator`)
16. **AI Career Network, Personal Brand & Referral Intelligence Engine** (`/api/v1/network`, `/api/v1/brand`)

---

## 🚀 Quick Start

### 1. Database Setup & Alembic Migrations
```powershell
cd backend
alembic upgrade head
```

### 2. Run Backend Server
```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation: `http://localhost:8000/docs`

### 3. Run Frontend Interface
Open `frontend/index.html` directly in your browser.
