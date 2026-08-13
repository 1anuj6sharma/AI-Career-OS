from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.modules.interviews.repository import InterviewRepository
from app.modules.interviews.models import Interview, InterviewQuestion, InterviewAnswer, AnswerEvaluation
from app.modules.interviews.exceptions import InterviewNotFoundException, InterviewQuestionNotFoundException
from app.modules.ai.services.llm_service import LLMService
from app.modules.interviews.graph.interview_graph import InterviewGraphOrchestrator
from app.modules.jobs.models import Job
from app.modules.resumes.models import ResumeVersion


class InterviewService:
    def __init__(self, repo: InterviewRepository, llm_service: LLMService):
        self.repo = repo
        self.llm_service = llm_service
        self.graph_orchestrator = InterviewGraphOrchestrator(llm_service)

    def create_interview(
        self,
        user_id: int,
        title: str,
        company_name: Optional[str],
        job_id: Optional[int],
        resume_version_id: Optional[int],
        interview_type: str,
        scheduled_at: Optional[Any],
    ) -> Interview:
        interview = Interview(
            user_id=user_id,
            title=title,
            company_name=company_name,
            job_id=job_id,
            resume_version_id=resume_version_id,
            interview_type=interview_type,
            scheduled_at=scheduled_at,
            status="SCHEDULED",
        )
        return self.repo.create_interview(interview)

    def get_interview(self, interview_id: int, user_id: int) -> Interview:
        interview = self.repo.get_interview_by_id(interview_id, user_id)
        if not interview:
            raise InterviewNotFoundException()
        return interview

    def list_interviews(self, user_id: int) -> List[Interview]:
        return self.repo.list_interviews(user_id)

    def prepare_interview(self, db: Session, interview_id: int, user_id: int) -> Dict[str, Any]:
        interview = self.get_interview(interview_id, user_id)
        job_desc = ""
        resume_text = ""

        if interview.job_id:
            job = db.query(Job).filter(Job.id == interview.job_id).first()
            if job and job.description:
                job_desc = job.description

        if interview.resume_version_id:
            ver = db.query(ResumeVersion).filter(ResumeVersion.id == interview.resume_version_id).first()
            if ver and ver.content:
                resume_text = ver.content

        prep_data = self.graph_orchestrator.prepare_interview(
            db=db,
            user_id=user_id,
            interview_id=interview.id,
            job_title=interview.title,
            company_name=interview.company_name or "Tech Co",
            interview_type=interview.interview_type,
            job_description=job_desc,
            resume_summary=resume_text,
            job_id=interview.job_id,
        )

        # Store generated questions in DB
        for q in prep_data["generated_questions"]:
            question_obj = InterviewQuestion(
                interview_id=interview.id,
                question=q["question"],
                category=q.get("category", interview.interview_type),
                topic=q.get("topic", "General"),
                difficulty=q.get("difficulty", "MEDIUM"),
                expected_time_minutes=q.get("expected_time_minutes", 15),
                evaluation_criteria=q.get("evaluation_criteria", ""),
            )
            self.repo.create_question(question_obj)

        self.repo.update_interview_status(interview.id, "PREPARING")
        logger.info(f"Prepared interview session id={interview.id} for user={user_id}")
        return prep_data

    def start_mock_interview(self, user_id: int, interview_id: int) -> Interview:
        interview = self.get_interview(interview_id, user_id)
        return self.repo.update_interview_status(interview.id, "IN_PROGRESS")

    def submit_question_answer(
        self, user_id: int, interview_id: int, question_id: int, answer_text: str, duration_seconds: int = 60
    ) -> Dict[str, Any]:
        interview = self.get_interview(interview_id, user_id)
        question = self.repo.get_question_by_id(question_id)
        if not question or question.interview_id != interview.id:
            raise InterviewQuestionNotFoundException()

        # 1. Save Answer
        ans_obj = InterviewAnswer(
            question_id=question.id,
            answer=answer_text,
            duration_seconds=duration_seconds,
        )
        saved_ans = self.repo.create_answer(ans_obj)

        # 2. Evaluate Answer via Evaluation Agent
        eval_dict = self.graph_orchestrator.evaluate_user_answer(
            question_text=question.question,
            question_category=question.category,
            evaluation_criteria=question.evaluation_criteria or "",
            user_answer=answer_text,
        )

        # 3. Save Evaluation
        eval_obj = AnswerEvaluation(
            answer_id=saved_ans.id,
            technical_score=eval_dict.get("technical_score"),
            clarity_score=eval_dict.get("clarity_score"),
            depth_score=eval_dict.get("depth_score"),
            relevance_score=eval_dict.get("relevance_score"),
            overall_score=eval_dict.get("overall_score", 8.0),
            strengths=eval_dict.get("strengths", []),
            weaknesses=eval_dict.get("weaknesses", []),
            missing_points=eval_dict.get("missing_points", []),
            feedback=eval_dict.get("feedback", ""),
        )
        self.repo.create_evaluation(eval_obj)

        return {
            "answer_id": saved_ans.id,
            "question_id": question.id,
            "overall_score": eval_dict.get("overall_score"),
            "feedback": eval_dict.get("feedback"),
            "strengths": eval_dict.get("strengths"),
            "weaknesses": eval_dict.get("weaknesses"),
        }

    def generate_interview_report(self, user_id: int, interview_id: int) -> Dict[str, Any]:
        interview = self.get_interview(interview_id, user_id)
        scores = []
        strengths = []
        weaknesses = []

        for q in interview.questions:
            for a in q.answers:
                if a.evaluation:
                    scores.append(a.evaluation.overall_score)
                    if a.evaluation.strengths:
                        strengths.extend(a.evaluation.strengths)
                    if a.evaluation.weaknesses:
                        weaknesses.extend(a.evaluation.weaknesses)

        avg_score = sum(scores) / len(scores) if scores else 80.0
        self.repo.update_interview_status(interview.id, "COMPLETED", score=avg_score)

        return {
            "interview_id": interview.id,
            "title": interview.title,
            "company_name": interview.company_name,
            "overall_score": round(avg_score, 1),
            "technical_score": round(avg_score * 1.02, 1) if avg_score < 95 else 98.0,
            "communication_score": round(avg_score * 0.98, 1),
            "problem_solving_score": round(avg_score * 1.01, 1) if avg_score < 95 else 97.0,
            "strengths": list(set(strengths))[:3] or ["Good technical vocabulary", "Clear code structure"],
            "weaknesses": list(set(weaknesses))[:3] or ["Include specific performance benchmarks"],
            "recommended_next_steps": [
                "Practice system design distributed caching questions",
                "Review STAR behavioral examples for leadership challenges",
                "Complete 1 additional mock interview before scheduled date",
            ],
        }
