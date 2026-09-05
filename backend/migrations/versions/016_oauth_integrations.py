"""oauth integrations

Revision ID: 016_oauth_integrations
Revises: 015_network_referral_brand
Create Date: 2026-09-02 06:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '016_oauth_integrations'
down_revision: Union[str, Sequence[str], None] = '015_network_referral_brand'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns
    op.add_column('user_integrations', sa.Column('provider', sa.String(length=50), nullable=True))
    op.add_column('user_integrations', sa.Column('provider_account_id', sa.String(length=255), nullable=True))
    op.add_column('user_integrations', sa.Column('provider_username', sa.String(length=255), nullable=True))
    op.add_column('user_integrations', sa.Column('display_name', sa.String(length=255), nullable=True))
    op.add_column('user_integrations', sa.Column('profile_url', sa.String(length=512), nullable=True))
    op.add_column('user_integrations', sa.Column('avatar_url', sa.String(length=512), nullable=True))
    op.add_column('user_integrations', sa.Column('refresh_token_encrypted', sa.String(length=2048), nullable=True))
    op.add_column('user_integrations', sa.Column('token_expires_at', sa.DateTime(), nullable=True))
    op.add_column('user_integrations', sa.Column('scopes', sa.String(length=1024), nullable=True))
    op.add_column('user_integrations', sa.Column('connection_status', sa.String(length=50), server_default="NOT_CONNECTED", nullable=False))
    op.add_column('user_integrations', sa.Column('last_sync_status', sa.String(length=50), nullable=True))
    op.add_column('user_integrations', sa.Column('last_error', sa.String(length=1024), nullable=True))
    
    # 2. Modify existing columns (increase access_token length)
    op.alter_column('user_integrations', 'access_token_encrypted',
               existing_type=sa.VARCHAR(length=512),
               type_=sa.String(length=2048),
               existing_nullable=True)
               
    # 3. Data migration (copy platform to provider)
    op.execute("UPDATE user_integrations SET provider = platform WHERE platform IS NOT NULL")
    op.execute("UPDATE user_integrations SET provider_account_id = identifier WHERE identifier IS NOT NULL")
    
    # 4. Make provider not nullable
    op.alter_column('user_integrations', 'provider',
               existing_type=sa.String(length=50),
               nullable=False)
               
    # 5. Drop old columns
    op.drop_index('ix_user_integrations_platform', table_name='user_integrations')
    op.drop_column('user_integrations', 'platform')
    op.drop_column('user_integrations', 'identifier')
    
    # 6. Create new index
    op.create_index(op.f('ix_user_integrations_provider'), 'user_integrations', ['provider'], unique=False)


def downgrade() -> None:
    op.add_column('user_integrations', sa.Column('identifier', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('user_integrations', sa.Column('platform', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    
    op.execute("UPDATE user_integrations SET platform = provider WHERE provider IS NOT NULL")
    op.execute("UPDATE user_integrations SET identifier = provider_account_id WHERE provider_account_id IS NOT NULL")
    
    op.alter_column('user_integrations', 'platform',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.alter_column('user_integrations', 'identifier',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
               
    op.create_index('ix_user_integrations_platform', 'user_integrations', ['platform'], unique=False)
    
    op.drop_index(op.f('ix_user_integrations_provider'), table_name='user_integrations')
    op.drop_column('user_integrations', 'last_error')
    op.drop_column('user_integrations', 'last_sync_status')
    op.drop_column('user_integrations', 'connection_status')
    op.drop_column('user_integrations', 'scopes')
    op.drop_column('user_integrations', 'token_expires_at')
    op.drop_column('user_integrations', 'refresh_token_encrypted')
    op.drop_column('user_integrations', 'avatar_url')
    op.drop_column('user_integrations', 'profile_url')
    op.drop_column('user_integrations', 'display_name')
    op.drop_column('user_integrations', 'provider_username')
    op.drop_column('user_integrations', 'provider_account_id')
    op.drop_column('user_integrations', 'provider')
    
    op.alter_column('user_integrations', 'access_token_encrypted',
               existing_type=sa.String(length=2048),
               type_=sa.VARCHAR(length=512),
               existing_nullable=True)
