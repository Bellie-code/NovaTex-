import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logger import logger


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration = round(time.time() - start_time, 4)

        logger.info(
            f"{request.method} {request.url.path} | "
            f"Status={response.status_code} | "
            f"Time={duration}s"
        )

        return response
