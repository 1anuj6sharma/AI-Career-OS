"""module 15 master orchestrator autonomous career agent

Revision ID: 014_master_orchestrator
Revises: 013_opportunity_acquisition
Create Date: 2026-08-14 13:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '014_master_orchestrator'
down_revision: Union[str, Sequence[str], None] = '013_opportunity_acquisition'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Master Career Plans Table
    op.create_table(
        'master_career_plans',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('goal_title', sa.String(length=200), nullable=False),
        sa.Column('strategy_summary', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_master_career_plans_user_id'), 'master_career_plans', ['user_id'], unique=False)
    op.create_index(op.f('ix_master_career_plans_status'), 'master_career_plans', ['status'], unique=False)

    # 2. Master Plan Steps Table
    op.create_table(
        'master_plan_steps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('module_name', sa.String(length=100), nullable=False),
        sa.Column('action_name', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('dependencies_json', sa.JSON(), nullable=True),
        sa.Column('result_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['master_career_plans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_master_plan_steps_plan_id'), 'master_plan_steps', ['plan_id'], unique=False)
    op.create_index(op.f('ix_master_plan_steps_module_name'), 'master_plan_steps', ['module_name'], unique=False)
    op.create_index(op.f('ix_master_plan_steps_status'), 'master_plan_steps', ['status'], unique=False)

    # 3. Master Career Decisions Table
    op.create_table(
        'master_career_decisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('decision_title', sa.String(length=200), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('required_modules_json', sa.JSON(), nullable=True),
        sa.Column('actions_json', sa.JSON(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.9'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='EXECUTED'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_master_career_decisions_user_id'), 'master_career_decisions', ['user_id'], unique=False)
    op.create_index(op.f('ix_master_career_decisions_status'), 'master_career_decisions', ['status'], unique=False)

    # 4. Master Career Events Table
    op.create_table(
        'master_career_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('source_module', sa.String(length=100), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_master_career_events_user_id'), 'master_career_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_master_career_events_event_type'), 'master_career_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_master_career_events_source_module'), 'master_career_events', ['source_module'], unique=False)

    # 5. Master Career Memory Table
    op.create_table(
        'master_career_memory',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('memory_type', sa.String(length=50), nullable=False, server_default='LONG_TERM'),
        sa.Column('key', sa.String(length=200), nullable=False),
        sa.Column('content_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_master_career_memory_user_id'), 'master_career_memory', ['user_id'], unique=False)
    op.create_index(op.f('ix_master_career_memory_memory_type'), 'master_career_memory', ['memory_type'], unique=False)
    op.create_index(op.f('ix_master_career_memory_key'), 'master_career_memory', ['key'], unique=False)

    # 6. Master Career Strategies Table
    op.create_table(
        'master_career_strategies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('strategy_title', sa.String(length=200), nullable=False),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('reasons_for_pivot', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_master_career_strategies_user_id'), 'master_career_strategies', ['user_id'], unique=False)
    op.create_index(op.f('ix_master_career_strategies_is_active'), 'master_career_strategies', ['is_active'], unique=False)

    # 7. Master Approvals Table
    op.create_table(
        'master_approvals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.String(length=100), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('action_description', sa.Text(), nullable=False),
        sa.Column('risk_level', sa.String(length=50), nullable=False, server_default='LEVEL_3'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING_APPROVAL'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_master_approvals_user_id'), 'master_approvals', ['user_id'], unique=False)
    op.create_index(op.f('ix_master_approvals_status'), 'master_approvals', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('master_approvals')
    op.drop_table('master_career_strategies')
    op.drop_table('master_career_memory')
    op.drop_table('master_career_events')
    op.drop_table('master_career_decisions')
    op.drop_table('master_plan_steps')
    op.drop_table('master_career_plans')
