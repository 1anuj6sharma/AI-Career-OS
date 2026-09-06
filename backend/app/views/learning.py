from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class LearningResourceOut(BaseModel):
    id: int
    topic_id: int
    title: str
    resource_type: str
    url: Optional[str] = None
    difficulty: str
    relevance_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningTopicOut(BaseModel):
    id: int
    module_id: int
    title: str
    difficulty: str
    estimated_minutes: int
    status: str
    resources: List[LearningResourceOut] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningModuleOut(BaseModel):
    id: int
    learning_path_id: int
    title: str
    description: Optional[str] = None
    sequence: int
    topics: List[LearningTopicOut] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LearningPathOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    status: str
    modules: List[LearningModuleOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TutorQuery(BaseModel):
    topic: str = Field("Docker Networking", example="Docker Networking")
    question: str = Field("Explain how Docker bridge networks work vs host networks.", example="Explain how Docker bridge networks work vs host networks.")
    mode: str = Field("INTERMEDIATE", example="INTERMEDIATE")  # BEGINNER, INTERMEDIATE, ADVANCED, INTERVIEW, PROJECT


class TutorResponse(BaseModel):
    topic: str
    explanation: str
    retrieved_docs_count: int
    suggested_practice: str
    code_example: Optional[str] = None


class PracticeChallengeOut(BaseModel):
    topic: str
    challenge_title: str
    problem_statement: str
    starter_code_or_config: Optional[str] = None
    verification_hints: List[str] = []


class AssessmentSubmitQuery(BaseModel):
    topic_id: Optional[int] = None
    topic_title: str = Field("Docker Networking", example="Docker Networking")
    submission_text: str = Field(..., min_length=5, example="Docker bridge network creates a virtual bridge interface on host to isolate containers.")


class LearningAssessmentOut(BaseModel):
    id: int
    topic_id: Optional[int] = None
    score: float
    feedback: str
    passed: bool
    remedial_action: Optional[str] = None
    created_at: datetime
