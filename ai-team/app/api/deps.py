"""Request dependencies."""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.common.config import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

_bearer = HTTPBearer(auto_error=False)


async def verify_service_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    """
    Check the shared token from Core Service.

    An empty token disables the check for local development;
    `validate_settings()` refuses to start in production without one.
    """
    if not settings.rag_service_token:
        return

    if credentials is None or credentials.scheme.lower() != "bearer":
        logger.warning("Request rejected: missing bearer token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Constant-time: a plain == leaks the token through timing.
    if not secrets.compare_digest(credentials.credentials, settings.rag_service_token):
        logger.warning("Request rejected: invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
