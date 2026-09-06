from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from cryptography.fernet import Fernet

from app.core.config import settings
from app.core.logging import logger
from app.models.integrations import UserIntegration
from app.controllers.integrations.providers import get_provider, OAuthProvider, PublicProfileProvider, ProviderError
from app.models.profile import Skill as ProfileSkill

class IntegrationService:
    def __init__(self):
        if settings.ENCRYPTION_KEY:
            self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())
        else:
            self.fernet = None
            logger.warning("ENCRYPTION_KEY is not set. Tokens will be stored in plaintext. This is insecure.")

    def _encrypt(self, text: Optional[str]) -> Optional[str]:
        if not text: return None
        if not self.fernet: return text
        return self.fernet.encrypt(text.encode()).decode()

    def _decrypt(self, text: Optional[str]) -> Optional[str]:
        if not text: return None
        if not self.fernet: return text
        try:
            return self.fernet.decrypt(text.encode()).decode()
        except Exception:
            return None

    def get_authorization_url(self, provider_name: str, state: str) -> str:
        provider = get_provider(provider_name)
        if not isinstance(provider, OAuthProvider):
            raise ValueError(f"{provider_name} does not support OAuth")
        return provider.get_authorization_url(state)

    async def handle_oauth_callback(
        self,
        db: Session,
        user_id: int,
        provider_name: str,
        code: str,
        redirect_uri: str
    ) -> UserIntegration:
        provider = get_provider(provider_name)
        if not isinstance(provider, OAuthProvider):
            raise ValueError("Provider is not an OAuth provider")

        try:
            # 1. Exchange code for tokens
            tokens = await provider.exchange_code(code, redirect_uri)
            access_token = tokens.get("access_token")
            
            # 2. Get user profile from provider
            profile = await provider.get_user_profile(access_token)
            
            # 3. Store integration
            integration = self._upsert_integration(
                db=db,
                user_id=user_id,
                provider_name=provider_name,
                profile=profile,
                access_token=access_token,
                refresh_token=tokens.get("refresh_token")
            )
            
            # 4. Trigger initial sync
            await self.sync_platform(db, user_id, provider_name)
            
            return integration
        except Exception as e:
            logger.error(f"OAuth callback failed for {provider_name}: {e}")
            raise

    async def link_public_profile(self, db: Session, user_id: int, provider_name: str, identifier: str) -> UserIntegration:
        provider = get_provider(provider_name)
        if not isinstance(provider, PublicProfileProvider):
            raise ValueError("Provider does not support public profile linking")
            
        try:
            profile = await provider.validate_and_get_profile(identifier)
            integration = self._upsert_integration(
                db=db,
                user_id=user_id,
                provider_name=provider_name,
                profile=profile
            )
            
            await self.sync_platform(db, user_id, provider_name)
            return integration
        except Exception as e:
            logger.error(f"Failed to link public profile {provider_name}: {e}")
            raise

    def _upsert_integration(
        self,
        db: Session,
        user_id: int,
        provider_name: str,
        profile: Dict[str, Any],
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None
    ) -> UserIntegration:
        stmt = select(UserIntegration).where(
            UserIntegration.user_id == user_id,
            UserIntegration.provider == provider_name
        )
        existing = db.execute(stmt).scalar_one_or_none()

        if existing:
            existing.provider_account_id = str(profile.get("provider_account_id"))
            existing.provider_username = profile.get("provider_username")
            existing.display_name = profile.get("display_name")
            existing.profile_url = profile.get("profile_url")
            existing.avatar_url = profile.get("avatar_url")
            existing.connection_status = "CONNECTED"
            existing.is_active = True
            
            if access_token:
                existing.access_token_encrypted = self._encrypt(access_token)
            if refresh_token:
                existing.refresh_token_encrypted = self._encrypt(refresh_token)
                
            integration = existing
        else:
            integration = UserIntegration(
                user_id=user_id,
                provider=provider_name,
                provider_account_id=str(profile.get("provider_account_id")),
                provider_username=profile.get("provider_username"),
                display_name=profile.get("display_name"),
                profile_url=profile.get("profile_url"),
                avatar_url=profile.get("avatar_url"),
                access_token_encrypted=self._encrypt(access_token),
                refresh_token_encrypted=self._encrypt(refresh_token),
                connection_status="CONNECTED",
                is_active=True,
                telemetry_data={}
            )
            db.add(integration)
        
        db.commit()
        db.refresh(integration)
        return integration

    async def sync_platform(self, db: Session, user_id: int, provider_name: str) -> Optional[UserIntegration]:
        stmt = select(UserIntegration).where(
            UserIntegration.user_id == user_id,
            UserIntegration.provider == provider_name,
            UserIntegration.is_active == True
        )
        integration = db.execute(stmt).scalar_one_or_none()
        if not integration:
            return None

        integration.connection_status = "SYNCING"
        db.commit()

        try:
            provider = get_provider(provider_name)
            
            if isinstance(provider, OAuthProvider):
                access_token = self._decrypt(integration.access_token_encrypted)
                telemetry = await provider.get_telemetry(access_token, integration.provider_username)
            elif isinstance(provider, PublicProfileProvider):
                telemetry = await provider.get_telemetry(integration.provider_username or integration.provider_account_id)
            else:
                telemetry = {}

            integration.telemetry_data = telemetry
            integration.last_synced_at = datetime.utcnow()
            integration.last_sync_status = "SUCCESS"
            integration.connection_status = "CONNECTED"
            
            self._sync_skills_from_telemetry(db, user_id, provider_name, telemetry)
            
        except Exception as e:
            logger.error(f"Sync failed for {provider_name}: {e}")
            integration.last_sync_status = "FAILED"
            integration.last_error = str(e)
            integration.connection_status = "SYNC_FAILED"

        db.commit()
        db.refresh(integration)
        return integration

    async def sync_all_user_integrations(self, db: Session, user_id: int) -> List[UserIntegration]:
        stmt = select(UserIntegration).where(
            UserIntegration.user_id == user_id,
            UserIntegration.is_active == True
        )
        active_list = list(db.execute(stmt).scalars().all())

        for integ in active_list:
            await self.sync_platform(db, user_id, integ.provider)

        db.commit()
        return active_list

    def disconnect_platform(self, db: Session, user_id: int, provider_name: str) -> bool:
        stmt = select(UserIntegration).where(
            UserIntegration.user_id == user_id,
            UserIntegration.provider == provider_name
        )
        integration = db.execute(stmt).scalar_one_or_none()
        if not integration:
            return False

        integration.is_active = False
        integration.connection_status = "DISCONNECTED"
        integration.access_token_encrypted = None
        integration.refresh_token_encrypted = None
        integration.telemetry_data = {}
        db.commit()
        return True

    def get_user_integrations_summary(self, db: Session, user_id: int) -> Dict[str, Any]:
        stmt = select(UserIntegration).where(UserIntegration.user_id == user_id)
        records = list(db.execute(stmt).scalars().all())

        supported_platforms = ["github", "linkedin", "leetcode", "gfg", "email", "kaggle", "huggingface", "google", "microsoft"]
        result = {}

        for p in supported_platforms:
            rec = next((r for r in records if r.provider == p and r.is_active), None)
            if rec:
                result[p] = {
                    "connected": True,
                    "provider": p,
                    "provider_username": rec.provider_username,
                    "display_name": rec.display_name,
                    "profile_url": rec.profile_url,
                    "connection_status": rec.connection_status,
                    "telemetry": rec.telemetry_data or {},
                    "last_synced_at": rec.last_synced_at.isoformat() if rec.last_synced_at else None,
                    "last_sync_status": rec.last_sync_status
                }
            else:
                result[p] = {
                    "connected": False,
                    "provider": p,
                    "provider_username": None,
                    "connection_status": "NOT_CONNECTED",
                    "telemetry": {},
                    "last_synced_at": None
                }

        total_connected = sum(1 for p in result.values() if p["connected"])
        return {
            "total_connected": total_connected,
            "platforms": result
        }

    def _sync_skills_from_telemetry(self, db: Session, user_id: int, provider: str, telemetry: Dict[str, Any]):
        try:
            skills_to_add = []
            if provider == "github":
                langs = telemetry.get("top_languages", [])
                for l in langs:
                    skills_to_add.append((l, "Technical", "Advanced"))
            elif provider == "leetcode":
                if telemetry.get("total_solved", 0) > 0:
                    skills_to_add = [("Data Structures", "Technical", "Expert"), ("Algorithms", "Technical", "Advanced")]

            for s_name, s_cat, s_prof in skills_to_add:
                stmt = select(ProfileSkill).where(ProfileSkill.user_id == user_id, ProfileSkill.name == s_name)
                existing = db.execute(stmt).scalar_one_or_none()
                if not existing:
                    new_skill = ProfileSkill(
                        user_id=user_id,
                        name=s_name,
                        category=s_cat,
                        proficiency_level=s_prof
                    )
                    db.add(new_skill)
        except Exception as e:
            logger.warn(f"Skill auto-injection note: {e}")
