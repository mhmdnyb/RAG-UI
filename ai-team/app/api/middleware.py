"""
FastAPI middleware for authentication and error handling.

Owner: Dev 7
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from common.config import settings
from common.logger import get_logger

logger = get_logger("rag.api.middleware")


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Validates the Authorization Bearer token on incoming requests
    to protected endpoints (POST /rag/query).

    Skips authentication for health check and docs endpoints.
    """

    SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        # Skip auth for non-protected paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Skip auth if no token is configured (development mode)
        if not settings.rag_service_token:
            return await call_next(request)

        # Validate Bearer token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            logger.warning(f"Missing Bearer token for {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing Authorization header"},
            )

        token = auth_header.removeprefix("Bearer ").strip()
        if token != settings.rag_service_token:
            logger.warning(f"Invalid token for {request.url.path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"},
            )

        return await call_next(request)
