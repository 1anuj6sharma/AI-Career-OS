"""module 9 portfolio branding

Revision ID: 008_portfolio_branding
Revises: 007_learning_hub
Create Date: 2026-08-13 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008_portfolio_branding'
down_revision: Union[str, Sequence[str], None] = '007_learning_hub'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Portfolio Profiles Table
    op.create_table(
        'portfolio_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('target_role', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolio_profiles_user_id'), 'portfolio_profiles', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_profiles_status'), 'portfolio_profiles', ['status'], unique=False)

    # 2. Portfolio Projects Table
    op.create_table(
        'portfolio_projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('architecture', sa.Text(), nullable=True),
        sa.Column('technologies', sa.JSON(), nullable=True),
        sa.Column('impact', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.9'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolio_projects_portfolio_id'), 'portfolio_projects', ['portfolio_id'], unique=False)

    # 3. Career Brand Profiles Table
    op.create_table(
        'career_brand_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('brand_statement', sa.Text(), nullable=False),
        sa.Column('target_role', sa.String(length=200), nullable=False),
        sa.Column('positioning', sa.Text(), nullable=True),
        sa.Column('core_strengths', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_brand_profiles_user_id'), 'career_brand_profiles', ['user_id'], unique=False)

    # 4. Brand Scores Table
    op.create_table(
        'brand_scores',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('portfolio_score', sa.Float(), nullable=False, server_default='80.0'),
        sa.Column('github_score', sa.Float(), nullable=False, server_default='75.0'),
        sa.Column('linkedin_score', sa.Float(), nullable=False, server_default='70.0'),
        sa.Column('project_score', sa.Float(), nullable=False, server_default='85.0'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='77.5'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_brand_scores_user_id'), 'brand_scores', ['user_id'], unique=False)

    # 5. Content Items Table
    op.create_table(
        'content_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False, server_default='ARTICLE'),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_items_user_id'), 'content_items', ['user_id'], unique=False)
    op.create_index(op.f('ix_content_items_status'), 'content_items', ['status'], unique=False)

    # 6. GitHub Analysis Table
    op.create_table(
        'github_analyses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('repository_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('activity_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('documentation_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_github_analyses_user_id'), 'github_analyses', ['user_id'], unique=False)

    # 7. Profile Recommendations Table
    op.create_table(
        'profile_recommendations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False, server_default='LINKEDIN'),
        sa.Column('recommendation_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='HIGH'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_recommendations_user_id'), 'profile_recommendations', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('profile_recommendations')
    op.drop_table('github_analyses')
    op.drop_table('content_items')
    op.drop_table('brand_scores')
    op.drop_table('career_brand_profiles')
    op.drop_table('portfolio_projects')
    op.drop_table('portfolio_profiles')
