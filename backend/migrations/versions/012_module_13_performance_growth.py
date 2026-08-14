"""module 13 career performance productivity continuous growth

Revision ID: 012_performance_growth
Revises: 011_offer_management
Create Date: 2026-08-14 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '012_performance_growth'
down_revision: Union[str, Sequence[str], None] = '011_offer_management'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Career Goals Table
    op.create_table(
        'career_goals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal_type', sa.String(length=50), nullable=False, server_default='LONG_TERM'),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='HIGH'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('target_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_goals_user_id'), 'career_goals', ['user_id'], unique=False)
    op.create_index(op.f('ix_career_goals_goal_type'), 'career_goals', ['goal_type'], unique=False)
    op.create_index(op.f('ix_career_goals_status'), 'career_goals', ['status'], unique=False)

    # Add goal_id to career_milestones table if not present
    op.add_column('career_milestones', sa.Column('goal_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_milestone_goal', 'career_milestones', 'career_goals', ['goal_id'], ['id'], ondelete='SET NULL')
    op.create_index(op.f('ix_career_milestones_goal_id'), 'career_milestones', ['goal_id'], unique=False)

    # 2. Career Tasks Table
    op.create_table(
        'career_tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('milestone_id', sa.Integer(), nullable=True),
        sa.Column('goal_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='MEDIUM'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('estimated_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['milestone_id'], ['career_milestones.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['goal_id'], ['career_goals.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_tasks_user_id'), 'career_tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_career_tasks_milestone_id'), 'career_tasks', ['milestone_id'], unique=False)
    op.create_index(op.f('ix_career_tasks_goal_id'), 'career_tasks', ['goal_id'], unique=False)
    op.create_index(op.f('ix_career_tasks_status'), 'career_tasks', ['status'], unique=False)

    # 3. Career Progress Table
    op.create_table(
        'career_progress',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('measurement', sa.JSON(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_progress_user_id'), 'career_progress', ['user_id'], unique=False)
    op.create_index(op.f('ix_career_progress_category'), 'career_progress', ['category'], unique=False)

    # 4. Skill Progress Table
    op.create_table(
        'skill_progress',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='50.0'),
        sa.Column('evidence_score', sa.Float(), nullable=False, server_default='50.0'),
        sa.Column('assessment_score', sa.Float(), nullable=False, server_default='50.0'),
        sa.Column('project_score', sa.Float(), nullable=False, server_default='50.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='STABLE'),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_progress_user_id'), 'skill_progress', ['user_id'], unique=False)
    op.create_index(op.f('ix_skill_progress_skill_name'), 'skill_progress', ['skill_name'], unique=False)

    # 5. Career Reviews Table
    op.create_table(
        'career_reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('review_type', sa.String(length=50), nullable=False, server_default='WEEKLY'),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('performance_score', sa.Float(), nullable=False, server_default='80.0'),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_reviews_user_id'), 'career_reviews', ['user_id'], unique=False)

    # 6. Career Risks Table
    op.create_table(
        'career_risks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('risk_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='MEDIUM'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('recommended_action', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_risks_user_id'), 'career_risks', ['user_id'], unique=False)

    # 7. Career Scenarios Table
    op.create_table(
        'career_scenarios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('scenario_name', sa.String(length=200), nullable=False),
        sa.Column('target_role', sa.String(length=200), nullable=False),
        sa.Column('assumptions', sa.JSON(), nullable=True),
        sa.Column('projection', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_scenarios_user_id'), 'career_scenarios', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('career_scenarios')
    op.drop_table('career_risks')
    op.drop_table('career_reviews')
    op.drop_table('skill_progress')
    op.drop_table('career_progress')
    op.drop_table('career_tasks')
    op.drop_constraint('fk_milestone_goal', 'career_milestones', type_='foreignkey')
    op.drop_column('career_milestones', 'goal_id')
    op.drop_table('career_goals')
