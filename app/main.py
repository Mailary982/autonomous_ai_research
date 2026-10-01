from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.health import router as health_router
from app.api.routes.research import router as research_router
from app.config.settings import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Evidence-grounded autonomous research and decision "
        "intelligence platform."
    ),
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add or propagate a request ID for observability."""
    request_id = request.headers.get("X-Request-ID", str(uuid4()))

    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """Return a sanitized error response."""
    request_id = getattr(request.state, "request_id", "unknown")

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )


app.include_router(
    health_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    research_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/")
def root():
    """Basic API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }