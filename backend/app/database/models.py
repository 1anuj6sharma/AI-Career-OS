"""
Import every SQLAlchemy model here.
Alembic discovers all models through this file.
"""
from app.models.auth import User, RefreshToken  # noqa: F401
from app.models.profile import (  # noqa: F401
    Profile,
    Skill,
    Education,
    Experience,
    Certification,
    CareerPreference,
)
from app.models.jobs import (  # noqa: F401
    Company,
    Contact,
    Job,
    Application,
    ApplicationEvent,
    JobNote,
    JobTask,
)
# from app.models.ai import (  # noqa: F401
#     AIRun,
#     AIToolCall,
#     AIConversation,
#     AIMessage,
#     AIMemory,
#     AIPendingAction,
# )
from app.models.resumes import (  # noqa: F401
    Resume,
    ResumeVersion,
)
from app.models.interviews import (  # noqa: F401
    Interview,
    InterviewQuestion,
    InterviewAnswer,
    AnswerEvaluation,
)
from app.models.career import (  # noqa: F401
    CareerRoadmap,
    CareerMilestone,
    CareerAdaptation,
)
from app.models.learning import (  # noqa: F401
    LearningPath,
    LearningModule,
    LearningTopic,
    LearningResource,
    LearningAssessment,
    LearningNote,
)
from app.models.brand import (  # noqa: F401
    PortfolioProfile,
    PortfolioProject,
    CareerBrandProfile,
    BrandScore,
    ContentItem,
    GitHubAnalysis,
    ProfileRecommendation,
)
from app.models.opportunities import (  # noqa: F401
    JobOpportunity,
    JobRequirementItem,
    JobMatch,
    ApplicationReadiness,
    JobRecommendationRecord,
    CompanyIntelligenceRecord,
)
from app.models.network import (  # noqa: F401
    ProfessionalContact,
    Relationship,
    NetworkInteraction,
    OutreachMessageRecord,
    FollowUpRecord,
)
from app.models.offers import (  # noqa: F401
    CareerOffer,
    OfferCompensation,
    OfferAnalysisRecord,
    OfferComparisonRecord,
    NegotiationStrategyRecord,
    CareerDecisionRecord,
)
from app.models.ai import (  # noqa: F401
    AIRun, AIToolCall, AIConversation, AIMessage, AIMemory, AIPendingAction,
)
from app.models.ai_coach import (  # noqa: F401
    CareerHealthScore, CareerMemory, CareerRecommendation, CareerCoachingSession,
)










