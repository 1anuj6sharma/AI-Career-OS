"""module 16 network referral intelligence personal brand

Revision ID: 015_network_referral_brand
Revises: 014_master_orchestrator
Create Date: 2026-08-14 13:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '015_network_referral_brand'
down_revision: Union[str, Sequence[str], None] = '014_master_orchestrator'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Referral Opportunities Table
    op.create_table(
        'referral_opportunities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='85.0'),
        sa.Column('relationship_score', sa.Float(), nullable=False, server_default='80.0'),
        sa.Column('referral_score', sa.Float(), nullable=False, server_default='82.5'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DETECTED'),
        sa.Column('recommended_action', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['opportunity_id'], ['job_opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['professional_contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_referral_opportunities_user_id'), 'referral_opportunities', ['user_id'], unique=False)
    op.create_index(op.f('ix_referral_opportunities_opportunity_id'), 'referral_opportunities', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_referral_opportunities_contact_id'), 'referral_opportunities', ['contact_id'], unique=False)
    op.create_index(op.f('ix_referral_opportunities_status'), 'referral_opportunities', ['status'], unique=False)

    # 2. Personal Brand Profiles Table
    op.create_table(
        'personal_brand_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('headline', sa.String(length=250), nullable=False),
        sa.Column('about_summary', sa.Text(), nullable=False),
        sa.Column('brand_score', sa.Float(), nullable=False, server_default='82.0'),
        sa.Column('positioning_tier', sa.String(length=100), nullable=False, server_default='Backend & AI Specialist'),
        sa.Column('strengths_json', sa.JSON(), nullable=True),
        sa.Column('weaknesses_json', sa.JSON(), nullable=True),
        sa.Column('recommendations_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personal_brand_profiles_user_id'), 'personal_brand_profiles', ['user_id'], unique=False)

    # 3. Content Ideas Table
    op.create_table(
        'content_ideas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('pillar_title', sa.String(length=200), nullable=False),
        sa.Column('topic', sa.String(length=250), nullable=False),
        sa.Column('content_format', sa.String(length=50), nullable=False, server_default='TECHNICAL_ARTICLE'),
        sa.Column('target_audience', sa.String(length=200), nullable=False),
        sa.Column('draft_text', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_ideas_user_id'), 'content_ideas', ['user_id'], unique=False)
    op.create_index(op.f('ix_content_ideas_status'), 'content_ideas', ['status'], unique=False)

    # 4. Network Analytics Table
    op.create_table(
        'network_analytics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_contacts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_relationships', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('response_rate_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('referrals_received', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conversion_rate_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('insights_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_network_analytics_user_id'), 'network_analytics', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_table('network_analytics')
    op.drop_table('content_ideas')
    op.drop_table('personal_brand_profiles')
    op.drop_table('referral_opportunities')
