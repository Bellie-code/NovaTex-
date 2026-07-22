from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse
from app.core.logger import logger


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Unhandled Error: {str(e)}")

            return JSONResponse(
                status_code=500,
                content={"error": "Internal Server Error", "detail": str(e)}
            )
