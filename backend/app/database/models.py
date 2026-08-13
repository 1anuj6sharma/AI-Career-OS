"""
Import every SQLAlchemy model here.
Alembic discovers all models through this file.
"""
from app.modules.auth.models import User, RefreshToken  # noqa: F401
from app.modules.profile.models import (  # noqa: F401
    Profile,
    Skill,
    Education,
    Experience,
    Certification,
    CareerPreference,
)
from app.modules.jobs.models import (  # noqa: F401
    Company,
    Contact,
    Job,
    Application,
    ApplicationEvent,
    JobNote,
    JobTask,
)
from app.modules.ai.models import (  # noqa: F401
    AIRun,
    AIToolCall,
    AIConversation,
    AIMessage,
    AIMemory,
    AIPendingAction,
)
from app.modules.resumes.models import (  # noqa: F401
    Resume,
    ResumeVersion,
)
from app.modules.interviews.models import (  # noqa: F401
    Interview,
    InterviewQuestion,
    InterviewAnswer,
    AnswerEvaluation,
)
from app.modules.career.models import (  # noqa: F401
    CareerRoadmap,
    CareerMilestone,
    CareerAdaptation,
)
from app.modules.learning.models import (  # noqa: F401
    LearningPath,
    LearningModule,
    LearningTopic,
    LearningResource,
    LearningAssessment,
    LearningNote,
)






