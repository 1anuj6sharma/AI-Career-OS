"""module 10 job matching

Revision ID: 009_job_matching
Revises: 008_portfolio_branding
Create Date: 2026-08-13 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '009_job_matching'
down_revision: Union[str, Sequence[str], None] = '008_portfolio_branding'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Job Opportunities Table
    op.create_table(
        'job_opportunities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source', sa.String(length=100), nullable=False, server_default='USER_IMPORTED'),
        sa.Column('external_job_id', sa.String(length=200), nullable=True),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('remote_status', sa.String(length=50), nullable=False, server_default='HYBRID'),
        sa.Column('salary_min', sa.Float(), nullable=True),
        sa.Column('salary_max', sa.Float(), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=False, server_default='FULL_TIME'),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Job Requirements Table
    op.create_table(
        'job_requirements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('skill', sa.String(length=100), nullable=False),
        sa.Column('requirement_type', sa.String(length=50), nullable=False, server_default='REQUIRED'),
        sa.Column('importance', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('minimum_experience', sa.Float(), nullable=True, server_default='0.0'),
        sa.ForeignKeyConstraint(['job_id'], ['job_opportunities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_requirements_job_id'), 'job_requirements', ['job_id'], unique=False)

    # 3. Job Matches Table
    op.create_table(
        'job_matches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('skill_match', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('experience_match', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('project_match', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('resume_match', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('career_match', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('overall_match', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job_opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_matches_user_id'), 'job_matches', ['user_id'], unique=False)
    op.create_index(op.f('ix_job_matches_job_id'), 'job_matches', ['job_id'], unique=False)

    # 4. Application Readiness Table
    op.create_table(
        'application_readiness',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('readiness_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('resume_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('skill_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('project_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('interview_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job_opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_readiness_user_id'), 'application_readiness', ['user_id'], unique=False)
    op.create_index(op.f('ix_application_readiness_job_id'), 'application_readiness', ['job_id'], unique=False)

    # 5. Job Recommendations Table
    op.create_table(
        'job_recommendations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('recommendation', sa.String(length=100), nullable=False, server_default='PREPARE THEN APPLY'),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='HIGH'),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('estimated_preparation_hours', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job_opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_recommendations_user_id'), 'job_recommendations', ['user_id'], unique=False)
    op.create_index(op.f('ix_job_recommendations_job_id'), 'job_recommendations', ['job_id'], unique=False)

    # 6. Company Intelligence Table
    op.create_table(
        'company_intelligence',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('technology_fit', sa.Float(), nullable=False, server_default='80.0'),
        sa.Column('career_growth', sa.Float(), nullable=False, server_default='85.0'),
        sa.Column('overall_fit', sa.Float(), nullable=False, server_default='82.5'),
        sa.Column('analysis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_intelligence_company_name'), 'company_intelligence', ['company_name'], unique=False)


def downgrade() -> None:
    op.drop_table('company_intelligence')
    op.drop_table('job_recommendations')
    op.drop_table('application_readiness')
    op.drop_table('job_matches')
    op.drop_table('job_requirements')
    op.drop_table('job_opportunities')
