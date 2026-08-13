"""module 12 offer management

Revision ID: 011_offer_management
Revises: 010_networking_crm
Create Date: 2026-08-13 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '011_offer_management'
down_revision: Union[str, Sequence[str], None] = '010_networking_crm'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Career Offers Table
    op.create_table(
        'career_offers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='RECEIVED'),
        sa.Column('offer_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('joining_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('document_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_offers_user_id'), 'career_offers', ['user_id'], unique=False)
    op.create_index(op.f('ix_career_offers_status'), 'career_offers', ['status'], unique=False)

    # 2. Offer Compensation Table
    op.create_table(
        'offer_compensation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('offer_id', sa.Integer(), nullable=False),
        sa.Column('base_salary', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('variable_salary', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('bonus', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('joining_bonus', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('equity', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('benefits', sa.Text(), nullable=True),
        sa.Column('total_ctc', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('guaranteed_compensation', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['offer_id'], ['career_offers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offer_compensation_offer_id'), 'offer_compensation', ['offer_id'], unique=False)

    # 3. Offer Analysis Table
    op.create_table(
        'offer_analysis',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('offer_id', sa.Integer(), nullable=False),
        sa.Column('compensation_score', sa.Float(), nullable=False, server_default='80.0'),
        sa.Column('career_fit_score', sa.Float(), nullable=False, server_default='85.0'),
        sa.Column('growth_score', sa.Float(), nullable=False, server_default='85.0'),
        sa.Column('company_score', sa.Float(), nullable=False, server_default='80.0'),
        sa.Column('location_score', sa.Float(), nullable=False, server_default='80.0'),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='15.0'),
        sa.Column('overall_score', sa.Float(), nullable=False, server_default='82.5'),
        sa.Column('analysis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['offer_id'], ['career_offers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offer_analysis_offer_id'), 'offer_analysis', ['offer_id'], unique=False)

    # 4. Offer Comparisons Table
    op.create_table(
        'offer_comparisons',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('offer_a_id', sa.Integer(), nullable=False),
        sa.Column('offer_b_id', sa.Integer(), nullable=False),
        sa.Column('comparison_data', sa.JSON(), nullable=False),
        sa.Column('recommended_offer_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offer_comparisons_user_id'), 'offer_comparisons', ['user_id'], unique=False)

    # 5. Negotiation Strategies Table
    op.create_table(
        'negotiation_strategies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('offer_id', sa.Integer(), nullable=False),
        sa.Column('target_compensation', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('minimum_compensation', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('leverage_score', sa.Float(), nullable=False, server_default='75.0'),
        sa.Column('priorities', sa.JSON(), nullable=True),
        sa.Column('strategy', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['offer_id'], ['career_offers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_negotiation_strategies_offer_id'), 'negotiation_strategies', ['offer_id'], unique=False)

    # 6. Career Decisions Table
    op.create_table(
        'career_decisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('offer_id', sa.Integer(), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False, server_default='NEGOTIATE'),
        sa.Column('reasoning', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='85.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['offer_id'], ['career_offers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_career_decisions_user_id'), 'career_decisions', ['user_id'], unique=False)
    op.create_index(op.f('ix_career_decisions_offer_id'), 'career_decisions', ['offer_id'], unique=False)


def downgrade() -> None:
    op.drop_table('career_decisions')
    op.drop_table('negotiation_strategies')
    op.drop_table('offer_comparisons')
    op.drop_table('offer_analysis')
    op.drop_table('offer_compensation')
    op.drop_table('career_offers')
