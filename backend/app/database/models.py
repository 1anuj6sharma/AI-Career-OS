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

