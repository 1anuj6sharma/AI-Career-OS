from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ai_coach import CareerCoachingSession, CareerHealthScore, CareerMemory, CareerRecommendation
from app.models.brand import BrandScore, PortfolioProfile, PortfolioProject
from app.models.career import CareerGoal, CareerMilestone, CareerRoadmap, CareerTask
from app.models.interviews import AnswerEvaluation, Interview, InterviewAnswer, InterviewQuestion
from app.models.jobs import Application, Contact, Job
from app.models.learning import LearningAssessment, LearningPath, LearningTopic
from app.models.profile import CareerPreference, Experience, Profile, Skill
from app.models.resumes import Resume, ResumeVersion


ROLE_REQUIREMENTS = {
    "ai": ["python", "machine learning", "llm", "fastapi", "sql", "docker", "rag", "system design"],
    "data": ["python", "sql", "statistics", "machine learning", "data modeling", "etl", "cloud"],
    "backend": ["python", "api", "sql", "postgresql", "docker", "testing", "system design", "cloud"],
    "frontend": ["javascript", "typescript", "react", "testing", "api", "css", "performance"],
    "product": ["product strategy", "analytics", "experimentation", "stakeholder management", "roadmap"],
}


class CoachState(TypedDict, total=False):
    user_id: int
    request: str
    context: Dict[str, Any]
    intent: str
    analysis: Dict[str, Any]
    response: Dict[str, Any]


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9+#.]", " ", (value or "").lower()).strip()


def _contains(text: str, phrase: str) -> bool:
    phrase = _normalize(phrase)
    return bool(phrase) and phrase in _normalize(text)


class CareerCoachService:
    """Evidence-first coach. It never invents user history when evidence is absent."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def context(self) -> Dict[str, Any]:
        profile = self.db.query(Profile).filter(Profile.user_id == self.user_id).first()
        preference = self.db.query(CareerPreference).filter(CareerPreference.user_id == self.user_id).first()
        skills = self.db.query(Skill).filter(Skill.user_id == self.user_id).all()
        experiences = self.db.query(Experience).filter(Experience.user_id == self.user_id).all()
        resumes = self.db.query(Resume).filter(Resume.user_id == self.user_id).all()
        versions = self.db.query(ResumeVersion).join(Resume).filter(Resume.user_id == self.user_id).all()
        portfolios = self.db.query(PortfolioProfile).filter(PortfolioProfile.user_id == self.user_id).all()
        portfolio_ids = [p.id for p in portfolios]
        projects = self.db.query(PortfolioProject).filter(PortfolioProject.portfolio_id.in_(portfolio_ids)).all() if portfolio_ids else []
        jobs = self.db.query(Job).filter(Job.user_id == self.user_id, Job.is_archived == False).all()
        applications = self.db.query(Application).filter(Application.user_id == self.user_id).all()
        interviews = self.db.query(Interview).filter(Interview.user_id == self.user_id).all()
        topic_rows = self.db.query(LearningTopic).join(LearningPath).filter(LearningPath.user_id == self.user_id).all()
        assessments = self.db.query(LearningAssessment).filter(LearningAssessment.user_id == self.user_id).all()
        contacts = self.db.query(Contact).filter(Contact.user_id == self.user_id).all()
        goals = self.db.query(CareerGoal).filter(CareerGoal.user_id == self.user_id, CareerGoal.status == "ACTIVE").all()
        tasks = self.db.query(CareerTask).filter(CareerTask.user_id == self.user_id).all()
        memories = self.db.query(CareerMemory).filter(CareerMemory.user_id == self.user_id).order_by(CareerMemory.updated_at.desc()).limit(20).all()
        role = (profile.target_role if profile and profile.target_role else None) or ((preference.target_roles or [None])[0] if preference else None) or ""
        return {
            "profile": profile, "preference": preference, "skills": skills, "experiences": experiences,
            "resumes": resumes, "versions": versions, "projects": projects, "jobs": jobs,
            "applications": applications, "interviews": interviews, "topics": topic_rows,
            "assessments": assessments, "contacts": contacts, "goals": goals, "tasks": tasks,
            "memories": memories, "target_role": role,
        }

    def requirements(self, context: Dict[str, Any]) -> List[str]:
        role = _normalize(context["target_role"])
        requirements: List[str] = []
        for signal, items in ROLE_REQUIREMENTS.items():
            if signal in role:
                requirements.extend(items)
        # Saved job descriptions are the primary market signal whenever available.
        matching_jobs = [j for j in context["jobs"] if not role or _contains(j.title, role) or _contains(role, j.title)]
        descriptions = " ".join((j.description or "") for j in matching_jobs or context["jobs"])
        known = {item for values in ROLE_REQUIREMENTS.values() for item in values}
        requirements.extend(item for item in known if _contains(descriptions, item))
        return list(dict.fromkeys(requirements))

    def skill_evidence(self, context: Dict[str, Any]) -> Dict[str, int]:
        evidence: Dict[str, int] = {}
        level = {"beginner": 35, "intermediate": 60, "advanced": 82, "expert": 95}
        for skill in context["skills"]:
            evidence[_normalize(skill.name)] = max(evidence.get(_normalize(skill.name), 0), level.get(_normalize(skill.proficiency_level), 50))
        supporting_text = " ".join(
            [e.description or "" for e in context["experiences"]]
            + [" ".join(e.technologies or []) for e in context["experiences"]]
            + [p.description or "" for p in context["projects"]]
            + [" ".join(p.technologies or []) for p in context["projects"]]
        )
        for item in self.requirements(context):
            key = _normalize(item)
            if _contains(supporting_text, item):
                evidence[key] = max(evidence.get(key, 0), 75)
        return evidence

    def health(self, persist: bool = True) -> Dict[str, Any]:
        c = self.context()
        evidence = self.skill_evidence(c)
        requirements = self.requirements(c)
        skills = round(sum(evidence.get(_normalize(r), 0) for r in requirements) / len(requirements)) if requirements else min(100, len(c["skills"]) * 12)
        experience = min(100, round(((c["profile"].years_of_experience or 0) * 15 if c["profile"] else 0) + len(c["experiences"]) * 12))
        resume_text = " ".join(v.content or "" for v in c["versions"])
        resume = 0 if not c["resumes"] else min(100, 45 + min(25, len(resume_text) // 250) + min(30, sum(_contains(resume_text, r) for r in requirements) * 5))
        brand = self.db.query(BrandScore).filter(BrandScore.user_id == self.user_id).order_by(BrandScore.created_at.desc()).first()
        portfolio = round(brand.portfolio_score) if brand else min(100, len(c["projects"]) * 25 + sum(bool(p.impact) + bool(p.architecture) for p in c["projects"]) * 8)
        evals = self.db.query(AnswerEvaluation).join(InterviewAnswer).join(InterviewQuestion).join(Interview).filter(Interview.user_id == self.user_id).all()
        interview = round(sum(e.overall_score for e in evals) / len(evals)) if evals else 0
        statuses = [_normalize(a.status) for a in c["applications"]]
        applied = sum(s in {"applied", "interview", "offer", "rejected"} for s in statuses)
        interview_count = sum(s in {"interview", "offer"} for s in statuses)
        offer_count = sum(s == "offer" for s in statuses)
        job_readiness = min(100, applied * 8 + len(c["jobs"]) * 3 + (20 if c["resumes"] else 0) + (15 if requirements else 0))
        application = 0 if not applied else min(100, round((interview_count / applied) * 65 + (offer_count / applied) * 35))
        market = 0 if not requirements else round(sum(evidence.get(_normalize(r), 0) for r in requirements) / len(requirements))
        networking = min(100, len(c["contacts"]) * 8)
        completed = sum(t.status == "COMPLETED" for t in c["topics"])
        learning = round((completed / len(c["topics"])) * 70 + (sum(a.score for a in c["assessments"]) / len(c["assessments"]) * .30 if c["assessments"] else 0)) if c["topics"] else 0
        metrics = {"Skills": skills, "Experience": experience, "Resume": resume, "Portfolio": portfolio, "Interview readiness": interview, "Job readiness": job_readiness, "Market alignment": market, "Networking": networking, "Learning progress": learning, "Application performance": application}
        weights = {"Skills": .16, "Experience": .10, "Resume": .11, "Portfolio": .10, "Interview readiness": .11, "Job readiness": .11, "Market alignment": .11, "Networking": .06, "Learning progress": .07, "Application performance": .07}
        total = round(sum(metrics[k] * weights[k] for k in metrics))
        result = {"total_score": total, "metrics": metrics, "calculated_at": datetime.utcnow().isoformat(), "data_coverage": sum(x > 0 for x in metrics.values())}
        if persist:
            score = CareerHealthScore(user_id=self.user_id, total_score=total, skills_score=skills, resume_score=resume, portfolio_score=portfolio, interview_score=interview, market_alignment_score=market, networking_score=networking, job_readiness_score=job_readiness, learning_progress_score=learning, application_performance_score=application, breakdown=metrics)
            self.db.add(score)
            self.db.commit()
        return result

    def gap_analysis(self) -> Dict[str, Any]:
        c = self.context()
        requirements, evidence = self.requirements(c), self.skill_evidence(c)
        source = "your saved target-role job descriptions" if c["jobs"] else "the role baseline; add target jobs for a market-specific analysis"
        gaps = []
        for requirement in requirements:
            score = evidence.get(_normalize(requirement), 0)
            priority = "CRITICAL" if score < 35 else "HIGH" if score < 60 else "MEDIUM"
            gaps.append({"skill": requirement, "current_score": score, "gap": 100 - score, "priority": priority, "why": f"{requirement.title()} appears in {source}.", "how_to_close": f"Create a focused evidence artifact using {requirement.title()} and add it to your resume or portfolio.", "estimated_time": "2–3 weeks" if score < 35 else "1 week"})
        gaps.sort(key=lambda x: x["gap"], reverse=True)
        return {"target_role": c["target_role"] or None, "source": source, "gaps": gaps[:8], "missing_data": [] if requirements else ["Set a target role or save a target job to unlock a role-specific gap analysis."]}

    def application_strategy(self) -> Dict[str, Any]:
        apps = self.context()["applications"]
        statuses = [_normalize(a.status) for a in apps]
        applied = sum(s in {"applied", "interview", "offer", "rejected"} for s in statuses)
        interviews = sum(s in {"interview", "offer"} for s in statuses)
        offers = sum(s == "offer" for s in statuses)
        rate = round(interviews / applied * 100, 1) if applied else None
        diagnosis = "Add applications and outcomes to unlock conversion analysis." if not applied else ("Your conversion data is still small; prioritize targeted applications and resume tailoring." if applied < 10 else ("Interview conversion is low relative to your recorded application volume; prioritize resume positioning and job targeting." if rate < 15 else "Your interview conversion is healthy; shift focus toward interview practice and follow-up."))
        return {"applications": applied, "interviews": interviews, "offers": offers, "interview_rate": rate, "diagnosis": diagnosis}

    def _recommendation_seed(self) -> Dict[str, Any]:
        c, health, gaps = self.context(), self.health(persist=False), self.gap_analysis()
        incomplete = [t for t in c["tasks"] if t.status in {"PENDING", "IN_PROGRESS", "POSTPONED"}]
        if incomplete:
            task = sorted(incomplete, key=lambda t: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(t.priority, 3), t.created_at))[0]
            return {"title": task.title, "rationale": task.description or "This is your highest-priority existing execution item.", "priority": task.priority, "impact": "HIGH" if task.priority == "HIGH" else "MEDIUM", "effort": "MEDIUM", "urgency": "HIGH", "estimated_minutes": task.estimated_minutes, "confidence": 88, "evidence": ["Existing career task", f"Career health: {health['total_score']}/100"], "task_id": task.id}
        if not c["resumes"]:
            return {"title": "Upload a resume to unlock evidence-based positioning", "rationale": "Resume intelligence is unavailable until the coach can read your actual resume.", "priority": "HIGH", "impact": "HIGH", "effort": "LOW", "urgency": "HIGH", "estimated_minutes": 10, "confidence": 96, "evidence": ["No resume on file"], "task_id": None}
        if gaps["gaps"]:
            gap = gaps["gaps"][0]
            return {"title": f"Build one portfolio artifact proving {gap['skill'].title()}", "rationale": f"{gap['skill'].title()} is your largest verified target-role gap. Evidence improves both recruiter screening and interview depth.", "priority": gap["priority"], "impact": "HIGH", "effort": "HIGH", "urgency": "HIGH", "estimated_minutes": 120, "confidence": 78, "evidence": [gap["why"], f"Current evidence: {gap['current_score']}%"], "task_id": None}
        return {"title": "Define a target role and save three target jobs", "rationale": "The coach needs a destination and market evidence before it can rank your next action.", "priority": "HIGH", "impact": "HIGH", "effort": "LOW", "urgency": "HIGH", "estimated_minutes": 20, "confidence": 94, "evidence": ["No target-role requirement signal"], "task_id": None}

    def next_action(self) -> Dict[str, Any]:
        seed = self._recommendation_seed()
        return {"id": None, **seed}

    def start_next_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        task_id = payload.get("task_id")
        if task_id:
            task = self.db.query(CareerTask).filter(CareerTask.id == task_id, CareerTask.user_id == self.user_id).first()
            if not task:
                raise ValueError("Task not found")
            task.status = "IN_PROGRESS"
        else:
            task = CareerTask(user_id=self.user_id, title=payload["title"], description=payload.get("rationale"), priority=payload.get("priority", "HIGH"), status="IN_PROGRESS", estimated_minutes=payload.get("estimated_minutes", 30))
            self.db.add(task)
            self.db.flush()
        rec = CareerRecommendation(user_id=self.user_id, recommendation_type="NEXT_ACTION", title=payload["title"], rationale=payload.get("rationale", ""), priority=payload.get("priority", "HIGH"), impact=payload.get("impact", "HIGH"), effort=payload.get("effort", "MEDIUM"), urgency=payload.get("urgency", "HIGH"), estimated_minutes=payload.get("estimated_minutes", 30), confidence=payload.get("confidence", 70), evidence=payload.get("evidence", []), task_id=task.id, status="ACCEPTED")
        self.db.add(rec)
        self.db.commit()
        return self.task_out(task)

    def task_out(self, task: CareerTask) -> Dict[str, Any]:
        return {"id": task.id, "title": task.title, "description": task.description, "priority": task.priority, "status": task.status, "estimated_minutes": task.estimated_minutes, "completed_at": task.completed_at.isoformat() if task.completed_at else None}

    def update_task(self, task_id: int, status: str) -> Dict[str, Any]:
        task = self.db.query(CareerTask).filter(CareerTask.id == task_id, CareerTask.user_id == self.user_id).first()
        if not task:
            raise ValueError("Task not found")
        if status not in {"PENDING", "IN_PROGRESS", "COMPLETED", "POSTPONED"}:
            raise ValueError("Invalid task status")
        task.status = status
        task.completed_at = datetime.utcnow() if status == "COMPLETED" else None
        self.db.commit()
        return self.task_out(task)

    def daily_brief(self) -> Dict[str, Any]:
        pending = [self.task_out(t) for t in self.context()["tasks"] if t.status in {"PENDING", "IN_PROGRESS"}][:5]
        return {"tasks": pending, "next_action": self.next_action(), "empty_state": None if pending else "No active tasks yet. Start your next best action to create a focused plan."}

    def weekly_strategy(self) -> Dict[str, Any]:
        current = self.health(persist=False)
        previous = self.db.query(CareerHealthScore).filter(CareerHealthScore.user_id == self.user_id).order_by(CareerHealthScore.calculated_at.desc()).offset(1).first()
        previous_metrics = previous.breakdown if previous and previous.breakdown else {}
        deltas = {key: value - previous_metrics.get(key, value) for key, value in current["metrics"].items()}
        best = max(deltas, key=deltas.get) if deltas else None
        worst = min(current["metrics"], key=current["metrics"].get)
        return {"what_improved": f"{best} changed by {deltas[best]:+.0f} points." if previous else "No previous snapshot yet—your first weekly comparison will appear after another analysis.", "what_got_worse": f"{min(deltas, key=deltas.get)} changed by {min(deltas.values()):+.0f} points." if previous and min(deltas.values()) < 0 else "No evidence-backed regression detected.", "biggest_opportunity": f"Improve {worst.lower()}, currently {current['metrics'][worst]}/100.", "biggest_risk": self.gap_analysis()["gaps"][0]["why"] if self.gap_analysis()["gaps"] else "Add a target role and job evidence to reveal risks.", "recommended_focus": self.next_action()["title"], "next_week_objectives": [self.next_action()["title"], "Complete or reschedule every active career task before adding new work."]}

    def job_match(self, job_id: int) -> Dict[str, Any]:
        job = self.db.query(Job).filter(Job.id == job_id, Job.user_id == self.user_id).first()
        if not job:
            raise ValueError("Job not found")
        c, evidence = self.context(), self.skill_evidence(self.context())
        text = f"{job.title} {job.description or ''}"
        candidate_terms = list(evidence.keys())
        matched = [term for term in candidate_terms if _contains(text, term)]
        job_terms = [term for term in set(sum(ROLE_REQUIREMENTS.values(), [])) if _contains(text, term)]
        missing = [term for term in job_terms if evidence.get(_normalize(term), 0) < 60]
        skill = round((len(matched) / max(1, len(job_terms))) * 100) if job_terms else min(80, len(c["skills"]) * 10)
        experience = min(100, round((c["profile"].years_of_experience or 0) * 20)) if c["profile"] else 0
        location = 100 if not job.location or not c["profile"] or not c["profile"].preferred_location or _contains(job.location, c["profile"].preferred_location) else 50
        resume = self.health(persist=False)["metrics"]["Resume"]
        score = round(skill * .45 + experience * .2 + resume * .2 + location * .15)
        return {"job_id": job.id, "job_title": job.title, "company": job.company_name, "match_score": score, "matched": matched[:8], "missing": missing[:8], "recommendation": "Apply — the recorded gaps are not critical blockers." if score >= 65 else "Strengthen the highlighted gaps or tailor evidence before applying.", "factors": {"skills": skill, "experience": experience, "location": location, "resume_alignment": resume}}

    def resume_analysis(self, job_id: Optional[int]) -> Dict[str, Any]:
        c = self.context()
        latest = sorted(c["versions"], key=lambda v: v.created_at or datetime.min, reverse=True)
        if not latest:
            return {"available": False, "message": "Upload a resume to unlock a resume-to-job analysis."}
        resume = latest[0]
        job = self.db.query(Job).filter(Job.id == job_id, Job.user_id == self.user_id).first() if job_id else None
        terms = [item for item in self.requirements(c) if job is None or _contains(f"{job.title} {job.description or ''}", item)]
        missing = [item for item in terms if not _contains(resume.content, item)]
        bullets = [line.strip() for line in (resume.content or "").splitlines() if line.strip().startswith(("-", "•"))]
        weak = [b for b in bullets if not re.search(r"\d|%|\$", b)][:4]
        score = round((len(terms) - len(missing)) / max(1, len(terms)) * 100)
        return {"available": True, "resume_id": resume.resume_id, "job_id": job.id if job else None, "match_score": score, "missing_keywords": missing, "weak_bullets": weak, "strong_bullets": [b for b in bullets if b not in weak][:4], "suggestions": ["Add evidence and metrics to weak bullets.", "Use only skills you can substantiate in an interview."]}

    def roadmap(self, days: int, target_role: Optional[str] = None) -> Dict[str, Any]:
        if days not in {30, 60, 90, 180, 365}:
            raise ValueError("Roadmap duration must be 30, 60, 90, 180, or 365 days")
        c = self.context()
        role = target_role or c["target_role"]
        if not role:
            raise ValueError("Set a target role before generating a roadmap")
        gaps = self.gap_analysis()["gaps"][:3]
        phases = [("Foundation", "Validate your target and close the highest-signal gap."), ("Skill development", "Practice the required skills deliberately."), ("Project building", "Turn learning into visible, interview-ready evidence."), ("Market preparation", "Tailor your resume and portfolio to target roles."), ("Job execution", "Apply selectively, follow up, and use feedback to recalibrate.")]
        old = self.db.query(CareerRoadmap).filter(CareerRoadmap.user_id == self.user_id, CareerRoadmap.status == "ACTIVE").all()
        for row in old:
            row.status = "ADAPTED"
        roadmap = CareerRoadmap(user_id=self.user_id, target_role=role, objective=f"Become ready for {role} in {days} days", status="ACTIVE", version=(max([r.version for r in old], default=0) + 1), roadmap_data={"duration_days": days, "phases": phases})
        self.db.add(roadmap)
        self.db.flush()
        generated_tasks = []
        for index, (name, description) in enumerate(phases):
            focus = gaps[min(index, len(gaps) - 1)]["skill"] if gaps else role
            milestone = CareerMilestone(roadmap_id=roadmap.id, title=f"Phase {index + 1}: {name}", description=f"{description} Focus: {focus}.", target_date=f"Day {round(days * (index + 1) / len(phases))}", priority="HIGH" if index < 3 else "MEDIUM")
            self.db.add(milestone)
            self.db.flush()
            task = CareerTask(user_id=self.user_id, milestone_id=milestone.id, title=f"{name}: {focus}", description=description, priority=milestone.priority, estimated_minutes=90)
            self.db.add(task)
            generated_tasks.append({"title": task.title, "phase": name})
        self.db.commit()
        return {"roadmap_id": roadmap.id, "target_role": role, "duration_days": days, "objective": roadmap.objective, "phases": [{"name": p[0], "description": p[1], "focus": gaps[min(i, len(gaps) - 1)]["skill"] if gaps else role} for i, p in enumerate(phases)], "tasks": generated_tasks}

    def start_interview(self, mode: str, job_id: Optional[int]) -> Dict[str, Any]:
        allowed = {"TECHNICAL", "BEHAVIORAL", "SYSTEM_DESIGN", "CODING", "HR", "CASE_STUDY"}
        mode = mode.upper()
        if mode not in allowed:
            raise ValueError("Unsupported interview mode")
        job = self.db.query(Job).filter(Job.id == job_id, Job.user_id == self.user_id).first() if job_id else None
        role = job.title if job else self.context()["target_role"] or "your target role"
        question = {"BEHAVIORAL": "Tell me about a time you changed direction after receiving difficult feedback. What was the outcome?", "SYSTEM_DESIGN": f"Design a production service for {role}. State requirements, trade-offs, data flow, and failure handling.", "CODING": "Talk through how you would choose a data structure, establish complexity, and test edge cases for a lookup-heavy problem.", "HR": f"Why are you pursuing {role}, and what evidence shows you are ready?", "CASE_STUDY": "Frame the problem, identify decision criteria, and explain your recommendation with risks.", "TECHNICAL": f"Explain a technically challenging decision you made that is relevant to {role}, including trade-offs."}[mode]
        interview = Interview(user_id=self.user_id, job_id=job.id if job else None, title=role, company_name=job.company_name if job else None, interview_type=mode, status="IN_PROGRESS")
        self.db.add(interview)
        self.db.flush()
        q = InterviewQuestion(interview_id=interview.id, question=question, category=mode, topic=role, evaluation_criteria="Structure, relevant evidence, trade-offs, and clear outcome.")
        self.db.add(q)
        self.db.commit()
        return {"interview_id": interview.id, "question_id": q.id, "mode": mode, "question": question}

    def answer_interview(self, interview_id: int, question_id: int, answer: str) -> Dict[str, Any]:
        question = self.db.query(InterviewQuestion).join(Interview).filter(InterviewQuestion.id == question_id, InterviewQuestion.interview_id == interview_id, Interview.user_id == self.user_id).first()
        if not question:
            raise ValueError("Interview question not found")
        text = _normalize(answer)
        clarity = min(100, 35 + min(35, len(answer.split()) // 4))
        depth = min(100, 25 + sum(term in text for term in ["trade off", "because", "metric", "risk", "scale", "result"]) * 12)
        technical = min(100, 30 + sum(term in text for term in ["architecture", "database", "api", "test", "latency", "cache", "algorithm"]) * 10)
        relevance = min(100, 45 + sum(term in text for term in _normalize(question.topic).split()) * 20)
        overall = round((clarity + depth + technical + relevance) / 4)
        weaknesses = []
        if depth < 60: weaknesses.append("Explain the trade-offs and risks behind your choice.")
        if "metric" not in text and not re.search(r"\d", answer): weaknesses.append("Add a measurable result or success criterion.")
        if len(answer.split()) < 45: weaknesses.append("Use a fuller structure: context, action, trade-off, and outcome.")
        response = InterviewAnswer(question_id=question.id, answer=answer)
        self.db.add(response)
        self.db.flush()
        evaluation = AnswerEvaluation(answer_id=response.id, technical_score=technical, clarity_score=clarity, depth_score=depth, relevance_score=relevance, overall_score=overall, strengths=["You addressed the prompt directly."] if relevance >= 60 else [], weaknesses=weaknesses, missing_points=weaknesses, feedback="Use a concise structure, explicitly name a trade-off, and close with the outcome.")
        self.db.add(evaluation)
        interview = self.db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == self.user_id).first()
        interview.overall_score = overall
        self.db.commit()
        return {"overall_score": overall, "scores": {"Communication": clarity, "Technical accuracy": technical, "Depth": depth, "Problem solving": relevance}, "weaknesses": weaknesses, "improved_answer_guidance": "Lead with the situation, describe your decision and trade-off, then state a measurable result.", "next_question": "What alternative did you reject, and why?"}

    def decision(self, question: str) -> Dict[str, Any]:
        c, health = self.context(), self.health(persist=False)
        q = _normalize(question)
        lowest = min(health["metrics"], key=health["metrics"].get)
        if "apply" in q:
            recommendation = "Apply selectively when you can show at least two directly relevant evidence points; tailor the resume first."
        elif "dsa" in q:
            recommendation = "Prioritize DSA when your target interviews explicitly test it; otherwise close your largest evidence gap first."
        elif "change job" in q:
            recommendation = "Prepare a targeted search before changing jobs: define the role, strengthen the weakest readiness dimension, and protect your financial runway."
        else:
            recommendation = f"Prioritize the option that improves {lowest.lower()} without delaying your stated target role."
        return {"recommendation": recommendation, "confidence": 68 if c["target_role"] else 42, "basis": [f"Target role: {c['target_role'] or 'not set'}", f"Lowest measured dimension: {lowest} ({health['metrics'][lowest]}/100)", "This is a planning recommendation, not a prediction."], "pros": ["Aligns effort to recorded career evidence."], "cons": ["Confidence is limited by missing context." if not c["target_role"] else "Requires consistent follow-through."], "risks": ["Do not treat the recommendation as a guarantee of a market outcome."], "next_action": self.next_action()["title"]}

    def store_memory(self, memory_type: str, content: str, context_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        memory = CareerMemory(user_id=self.user_id, memory_type=memory_type.upper(), content=content.strip(), context_data=context_data)
        self.db.add(memory)
        self.db.commit()
        return {"id": memory.id, "memory_type": memory.memory_type, "content": memory.content}

    def feedback(self, recommendation_id: int, value: str) -> Dict[str, Any]:
        recommendation = self.db.query(CareerRecommendation).filter(CareerRecommendation.id == recommendation_id, CareerRecommendation.user_id == self.user_id).first()
        if not recommendation:
            raise ValueError("Recommendation not found")
        if value not in {"HELPFUL", "NOT_HELPFUL"}:
            raise ValueError("Feedback must be HELPFUL or NOT_HELPFUL")
        recommendation.feedback = value
        self.db.commit()
        return {"id": recommendation.id, "feedback": value}

    def chat(self, request: str) -> Dict[str, Any]:
        started = datetime.utcnow()
        graph = self._graph()
        result = graph.invoke({"user_id": self.user_id, "request": request})
        response = result["response"]
        self.db.add(CareerCoachingSession(user_id=self.user_id, intent=result["intent"], request=request, response=response["answer"], context_summary=response.get("evidence"), latency_ms=int((datetime.utcnow() - started).total_seconds() * 1000)))
        self.db.commit()
        return response

    def _graph(self):
        builder = StateGraph(CoachState)
        builder.add_node("retrieve_context", lambda state: {"context": self.context()})
        builder.add_node("classify_intent", self._classify)
        builder.add_node("analyze", self._analyze)
        builder.add_node("respond", self._respond)
        builder.set_entry_point("retrieve_context")
        builder.add_edge("retrieve_context", "classify_intent")
        builder.add_edge("classify_intent", "analyze")
        builder.add_edge("analyze", "respond")
        builder.add_edge("respond", END)
        return builder.compile()

    def _classify(self, state: CoachState) -> Dict[str, Any]:
        text = _normalize(state["request"])
        intent = "career"
        if any(word in text for word in ["resume", "cv", "ats"]): intent = "resume"
        elif any(word in text for word in ["interview", "mock", "answer"]): intent = "interview"
        elif any(word in text for word in ["gap", "skills", "learn"]): intent = "gaps"
        elif any(word in text for word in ["roadmap", "90 day", "30 day", "60 day"]): intent = "roadmap"
        elif any(word in text for word in ["should i", "decision", "change jobs", "mba"]): intent = "decision"
        elif any(word in text for word in ["today", "next", "focus"]): intent = "next_action"
        return {"intent": intent}

    def _analyze(self, state: CoachState) -> Dict[str, Any]:
        handlers = {"resume": lambda: self.resume_analysis(None), "gaps": self.gap_analysis, "roadmap": lambda: {"next_action": self.next_action(), "note": "Choose a duration to generate an executable roadmap."}, "decision": lambda: self.decision(state["request"]), "next_action": self.next_action, "interview": lambda: {"note": "Choose an interview mode to start a persisted mock interview."}, "career": lambda: {"health": self.health(persist=False), "strategy": self.weekly_strategy(), "next_action": self.next_action()}}
        return {"analysis": handlers[state["intent"]]()}

    def _respond(self, state: CoachState) -> Dict[str, Any]:
        analysis, intent = state["analysis"], state["intent"]
        if intent == "next_action": answer = f"Recommendation: {analysis['title']}\n\nWhy: {analysis['rationale']}\n\nExpected impact: {analysis['impact']}"
        elif intent == "gaps": answer = "Recommendation: close the largest verified gap first.\n\n" + (f"{analysis['gaps'][0]['skill'].title()} is the highest-priority gap: {analysis['gaps'][0]['why']}" if analysis["gaps"] else analysis["missing_data"][0])
        elif intent == "resume": answer = analysis.get("message") or f"Recommendation: address {len(analysis['missing_keywords'])} missing job-relevant keywords and strengthen {len(analysis['weak_bullets'])} bullets with evidence."
        elif intent == "decision": answer = analysis["recommendation"]
        elif intent == "interview": answer = analysis["note"]
        elif intent == "roadmap": answer = analysis["note"]
        else: answer = f"Recommendation: {analysis['next_action']['title']}\n\nWhy: {analysis['next_action']['rationale']}"
        return {"response": {"intent": intent, "answer": answer, "analysis": analysis, "evidence": ["Authenticated user profile and connected Career OS records only"], "confidence": analysis.get("confidence", 75) if isinstance(analysis, dict) else 75}}
