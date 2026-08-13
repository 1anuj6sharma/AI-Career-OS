"""module 11 networking crm

Revision ID: 010_networking_crm
Revises: 009_job_matching
Create Date: 2026-08-13 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '010_networking_crm'
down_revision: Union[str, Sequence[str], None] = '009_job_matching'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Professional Contacts Table
    op.create_table(
        'professional_contacts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=200), nullable=False),
        sa.Column('company', sa.String(length=200), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('profile_url', sa.String(length=500), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False, server_default='USER_PROVIDED'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_professional_contacts_user_id'), 'professional_contacts', ['user_id'], unique=False)

    # 2. Relationships Table
    op.create_table(
        'relationships',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=100), nullable=False, server_default='RECRUITER'),
        sa.Column('relationship_strength', sa.String(length=50), nullable=False, server_default='WEAK'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='NEW'),
        sa.Column('last_interaction_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_follow_up_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['professional_contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_relationships_user_id'), 'relationships', ['user_id'], unique=False)
    op.create_index(op.f('ix_relationships_contact_id'), 'relationships', ['contact_id'], unique=False)
    op.create_index(op.f('ix_relationships_status'), 'relationships', ['status'], unique=False)

    # 3. Network Interactions Table
    op.create_table(
        'network_interactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('relationship_id', sa.Integer(), nullable=False),
        sa.Column('interaction_type', sa.String(length=50), nullable=False, server_default='MESSAGE'),
        sa.Column('direction', sa.String(length=50), nullable=False, server_default='OUTBOUND'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['relationship_id'], ['relationships.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_network_interactions_relationship_id'), 'network_interactions', ['relationship_id'], unique=False)

    # 4. Outreach Messages Table
    op.create_table(
        'outreach_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('purpose', sa.String(length=100), nullable=False, server_default='RECRUITER_OUTREACH'),
        sa.Column('subject', sa.String(length=200), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['professional_contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_outreach_messages_user_id'), 'outreach_messages', ['user_id'], unique=False)
    op.create_index(op.f('ix_outreach_messages_contact_id'), 'outreach_messages', ['contact_id'], unique=False)
    op.create_index(op.f('ix_outreach_messages_status'), 'outreach_messages', ['status'], unique=False)

    # 5. Follow Ups Table
    op.create_table(
        'follow_ups',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('related_opportunity_id', sa.Integer(), nullable=True),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['professional_contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_follow_ups_user_id'), 'follow_ups', ['user_id'], unique=False)
    op.create_index(op.f('ix_follow_ups_contact_id'), 'follow_ups', ['contact_id'], unique=False)


def downgrade() -> None:
    op.drop_table('follow_ups')
    op.drop_table('outreach_messages')
    op.drop_table('network_interactions')
    op.drop_table('relationships')
    op.drop_table('professional_contacts')
