import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core import auth

logger = logging.getLogger("sliding_expiration")


class SlidingExpirationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            try:
                payload, refreshed_token = auth.verify_and_refresh_token(token)
                logger.info(f"Token verified for user: {payload.get('sub')}")
                request.state.user = payload

                response = await call_next(request)

                response.headers["Authorization"] = f"Bearer {refreshed_token}"
                return response

            except HTTPException as e:
                logger.warning(f"Token verification failed: {e.detail}")
                raise
        else:
            logger.info("No Authorization header or wrong format")
            return await call_next(request)