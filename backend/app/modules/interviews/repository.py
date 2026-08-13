from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.modules.interviews.models import Interview, InterviewQuestion, InterviewAnswer, AnswerEvaluation


class InterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_interview(self, interview: Interview) -> Interview:
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def get_interview_by_id(self, interview_id: int, user_id: int) -> Optional[Interview]:
        return (
            self.db.query(Interview)
            .options(
                joinedload(Interview.questions)
                .joinedload(InterviewQuestion.answers)
                .joinedload(InterviewAnswer.evaluation)
            )
            .filter(Interview.id == interview_id, Interview.user_id == user_id)
            .first()
        )

    def list_interviews(self, user_id: int) -> List[Interview]:
        return (
            self.db.query(Interview)
            .options(
                joinedload(Interview.questions)
                .joinedload(InterviewQuestion.answers)
                .joinedload(InterviewAnswer.evaluation)
            )
            .filter(Interview.user_id == user_id)
            .order_by(Interview.created_at.desc())
            .all()
        )

    def create_question(self, question: InterviewQuestion) -> InterviewQuestion:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_question_by_id(self, question_id: int) -> Optional[InterviewQuestion]:
        return (
            self.db.query(InterviewQuestion)
            .options(
                joinedload(InterviewQuestion.answers)
                .joinedload(InterviewAnswer.evaluation)
            )
            .filter(InterviewQuestion.id == question_id)
            .first()
        )

    def create_answer(self, answer: InterviewAnswer) -> InterviewAnswer:
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def create_evaluation(self, evaluation: AnswerEvaluation) -> AnswerEvaluation:
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def update_interview_status(self, interview_id: int, status_name: str, score: Optional[float] = None) -> Interview:
        interview = self.db.query(Interview).filter(Interview.id == interview_id).first()
        if interview:
            interview.status = status_name
            if score is not None:
                interview.overall_score = score
            self.db.commit()
            self.db.refresh(interview)
        return interview
