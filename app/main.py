from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.routes import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.utils.dependencies import get_rate_limit_key

# Setup custom logging
setup_logging()

# Setup rate limiting
limiter = Limiter(key_func=get_rate_limit_key)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Monitoring"])
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}