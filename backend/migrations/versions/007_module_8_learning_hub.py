"""module 8 learning hub

Revision ID: 007_learning_hub
Revises: 006_career_execution
Create Date: 2026-08-13 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007_learning_hub'
down_revision: Union[str, Sequence[str], None] = '006_career_execution'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Learning Paths Table
    op.create_table(
        'learning_paths',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_paths_user_id'), 'learning_paths', ['user_id'], unique=False)
    op.create_index(op.f('ix_learning_paths_status'), 'learning_paths', ['status'], unique=False)

    # 2. Learning Modules Table
    op.create_table(
        'learning_modules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('learning_path_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['learning_path_id'], ['learning_paths.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_modules_learning_path_id'), 'learning_modules', ['learning_path_id'], unique=False)

    # 3. Learning Topics Table
    op.create_table(
        'learning_topics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default='INTERMEDIATE'),
        sa.Column('estimated_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['learning_modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_topics_module_id'), 'learning_topics', ['module_id'], unique=False)

    # 4. Learning Resources Table
    op.create_table(
        'learning_resources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False, server_default='DOCUMENTATION'),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default='INTERMEDIATE'),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='90.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['topic_id'], ['learning_topics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_resources_topic_id'), 'learning_resources', ['topic_id'], unique=False)

    # 5. Learning Assessments Table
    op.create_table(
        'learning_assessments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=True),
        sa.Column('score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['topic_id'], ['learning_topics.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_assessments_user_id'), 'learning_assessments', ['user_id'], unique=False)

    # 6. Learning Notes Table
    op.create_table(
        'learning_notes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('topic_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['topic_id'], ['learning_topics.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_notes_user_id'), 'learning_notes', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('learning_notes')
    op.drop_table('learning_assessments')
    op.drop_table('learning_resources')
    op.drop_table('learning_topics')
    op.drop_table('learning_modules')
    op.drop_table('learning_paths')
