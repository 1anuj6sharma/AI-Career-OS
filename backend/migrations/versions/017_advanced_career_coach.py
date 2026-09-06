"""advanced career coach persistence

Revision ID: 017_advanced_career_coach
Revises: 016_oauth_integrations
"""
from alembic import op
import sqlalchemy as sa


revision = "017_advanced_career_coach"
down_revision = "016_oauth_integrations"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    # These first two tables existed as ORM prototypes before they were migration-managed.
    if not _has_table("career_health_scores"):
        op.create_table(
            "career_health_scores",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("skills_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("resume_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("portfolio_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("interview_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("market_alignment_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("networking_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("job_readiness_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("learning_progress_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("application_performance_score", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("breakdown", sa.JSON(), nullable=True),
            sa.Column("calculated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_career_health_scores_user_id", "career_health_scores", ["user_id"])
    else:
        for name in ("job_readiness_score", "learning_progress_score", "application_performance_score"):
            if not _has_column("career_health_scores", name):
                op.add_column("career_health_scores", sa.Column(name, sa.Integer(), nullable=False, server_default="0"))
        if not _has_column("career_health_scores", "breakdown"):
            op.add_column("career_health_scores", sa.Column("breakdown", sa.JSON(), nullable=True))

    if not _has_table("career_memories"):
        op.create_table(
            "career_memories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("memory_type", sa.String(length=50), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("context_data", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_career_memories_user_id", "career_memories", ["user_id"])

    if not _has_table("career_recommendations"):
        op.create_table(
            "career_recommendations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("recommendation_type", sa.String(length=50), nullable=False),
            sa.Column("title", sa.String(length=300), nullable=False),
            sa.Column("rationale", sa.Text(), nullable=False),
            sa.Column("priority", sa.String(length=20), nullable=False),
            sa.Column("impact", sa.String(length=20), nullable=False),
            sa.Column("effort", sa.String(length=20), nullable=False),
            sa.Column("urgency", sa.String(length=20), nullable=False),
            sa.Column("estimated_minutes", sa.Integer(), nullable=False),
            sa.Column("confidence", sa.Integer(), nullable=False),
            sa.Column("evidence", sa.JSON(), nullable=True),
            sa.Column("task_id", sa.Integer(), sa.ForeignKey("career_tasks.id", ondelete="SET NULL"), nullable=True),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("feedback", sa.String(length=20), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_career_recommendations_user_id", "career_recommendations", ["user_id"])
        op.create_index("ix_career_recommendations_status", "career_recommendations", ["status"])
        
    if not _has_table("career_coaching_sessions"):
        op.create_table(
            "career_coaching_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("intent", sa.String(length=50), nullable=False),
            sa.Column("request", sa.Text(), nullable=False),
            sa.Column("response", sa.Text(), nullable=False),
            sa.Column("context_summary", sa.JSON(), nullable=True),
            sa.Column("latency_ms", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_career_coaching_sessions_user_id", "career_coaching_sessions", ["user_id"])


def downgrade() -> None:
    op.drop_table("career_coaching_sessions")
    op.drop_table("career_recommendations")
    # Existing prototype tables deliberately remain on downgrade to avoid deleting user memories.
