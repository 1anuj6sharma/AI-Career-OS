"""
Token Service

Responsible for JWT operations.
"""

from typing import Dict

from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TokenService:

    @staticmethod
    def generate_tokens(payload: Dict):

        access = create_access_token(payload)

        refresh = create_refresh_token(payload)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }

    @staticmethod
    def verify_token(token: str):

        return decode_token(token)
