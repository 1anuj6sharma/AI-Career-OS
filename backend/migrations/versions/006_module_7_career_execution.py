"""module 7 career execution

Revision ID: 006_career_execution
Revises: 005_interview_intelligence
Create Date: 2026-08-13 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_career_execution'
down_revision: Union[str, Sequence[str], None] = '005_interview_intelligence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Career Roadmaps Table
    op.create_table(
        'career_roadmaps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_role', sa.String(length=200), nullable=False),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('roadmap_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_roadmaps_user_id'), 'career_roadmaps', ['user_id'], unique=False)
    op.create_index(op.f('ix_career_roadmaps_status'), 'career_roadmaps', ['status'], unique=False)

    # 2. Career Milestones Table
    op.create_table(
        'career_milestones',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('roadmap_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_date', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='HIGH'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['roadmap_id'], ['career_roadmaps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_milestones_roadmap_id'), 'career_milestones', ['roadmap_id'], unique=False)

    # 3. Career Adaptations Table
    op.create_table(
        'career_adaptations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('roadmap_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('adaptation_summary', sa.Text(), nullable=False),
        sa.Column('changes_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['roadmap_id'], ['career_roadmaps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_adaptations_roadmap_id'), 'career_adaptations', ['roadmap_id'], unique=False)


def downgrade() -> None:
    op.drop_table('career_adaptations')
    op.drop_table('career_milestones')
    op.drop_table('career_roadmaps')
