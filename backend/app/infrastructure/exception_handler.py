"""Global exception handlers for the API."""

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.infrastructure.logger import logger

async def global_exception_handler(request: Request, exc: Exception):
    """Return JSON API errors and log them."""

    if isinstance(exc, HTTPException):
        logger.error(
            "HTTPException: %s - %s while processing %s %s",
            exc.status_code,
            exc.detail,
            request.method,
            request.url,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": f"HTTP {exc.status_code} Error", "message": exc.detail},
        )

    if isinstance(exc, RequestValidationError):
        logger.error("Validation error on %s %s: %s", request.method, request.url, exc.errors())
        return JSONResponse(
            status_code=422,
            content={"error": "Validation Error", "message": exc.errors()},
        )

    logger.exception(
        "Unhandled exception while processing %s %s", request.method, request.url
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "Unexpected error"},
    )
