"""module 14 opportunity intelligence job acquisition engine

Revision ID: 013_opportunity_acquisition
Revises: 012_performance_growth
Create Date: 2026-08-14 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '013_opportunity_acquisition'
down_revision: Union[str, Sequence[str], None] = '012_performance_growth'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Opportunity Scores Table
    op.create_table(
        'opportunity_scores',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=False),
        sa.Column('skill_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('experience_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('career_alignment_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('compensation_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('growth_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('company_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['opportunity_id'], ['job_opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_opportunity_scores_opportunity_id'), 'opportunity_scores', ['opportunity_id'], unique=False)

    # 2. Application Strategies Table
    op.create_table(
        'application_strategies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=True),
        sa.Column('target_role', sa.String(length=200), nullable=False),
        sa.Column('suggested_highlights', sa.JSON(), nullable=True),
        sa.Column('cover_letter_recommended', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('strategy_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['opportunity_id'], ['job_opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_strategies_user_id'), 'application_strategies', ['user_id'], unique=False)
    op.create_index(op.f('ix_application_strategies_opportunity_id'), 'application_strategies', ['opportunity_id'], unique=False)

    # 3. Module 14 Applications Table
    op.create_table(
        'module14_applications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=True),
        sa.Column('cover_letter_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PREPARED'),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False, server_default='AI_CAREER_OS'),
        sa.Column('external_application_id', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['opportunity_id'], ['job_opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_module14_applications_user_id'), 'module14_applications', ['user_id'], unique=False)
    op.create_index(op.f('ix_module14_applications_opportunity_id'), 'module14_applications', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_module14_applications_status'), 'module14_applications', ['status'], unique=False)

    # 4. Application Events Table
    op.create_table(
        'module14_application_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['module14_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_module14_application_events_application_id'), 'module14_application_events', ['application_id'], unique=False)
    op.create_index(op.f('ix_module14_application_events_event_type'), 'module14_application_events', ['event_type'], unique=False)

    # 5. Application Documents Table
    op.create_table(
        'application_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False, server_default='RESUME'),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['module14_applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_documents_application_id'), 'application_documents', ['application_id'], unique=False)

    # 6. Application Feedback Table
    op.create_table(
        'application_feedback',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('analysis_summary', sa.Text(), nullable=False),
        sa.Column('insights_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_feedback_user_id'), 'application_feedback', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('application_feedback')
    op.drop_table('application_documents')
    op.drop_table('module14_application_events')
    op.drop_table('module14_applications')
    op.drop_table('application_strategies')
    op.drop_table('opportunity_scores')
