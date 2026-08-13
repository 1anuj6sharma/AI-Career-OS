"""module 5 resume intelligence

Revision ID: 004_resume_intelligence
Revises: 003_ai_intelligence
Create Date: 2026-08-13 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_resume_intelligence'
down_revision: Union[str, Sequence[str], None] = '003_ai_intelligence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Resumes Table
    op.create_table(
        'resumes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=False, server_default='pdf'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PARSED'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resumes_user_id'), 'resumes', ['user_id'], unique=False)
    op.create_index(op.f('ix_resumes_status'), 'resumes', ['status'], unique=False)

    # 2. Resume Versions Table
    op.create_table(
        'resume_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('version_name', sa.String(length=200), nullable=False, server_default='v1.0 Original'),
        sa.Column('parent_version_id', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.String(length=50), nullable=False, server_default='USER'),
        sa.Column('generation_reason', sa.String(length=255), nullable=True),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('structured_data', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_versions_resume_id'), 'resume_versions', ['resume_id'], unique=False)
    op.create_index(op.f('ix_resume_versions_job_id'), 'resume_versions', ['job_id'], unique=False)

    # 3. Add resume_version_id to applications table
    op.add_column('applications', sa.Column('resume_version_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_applications_resume_version', 'applications', 'resume_versions', ['resume_version_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_constraint('fk_applications_resume_version', 'applications', type_='foreignkey')
    op.drop_column('applications', 'resume_version_id')
    op.drop_table('resume_versions')
    op.drop_table('resumes')
