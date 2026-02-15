"""FastAPI web application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.web.routes import router as api_router

app = FastAPI(
    title="TeamFlow API",
    version=settings.VERSION,
    description="Read-only API for TeamFlow task management"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],  # Read-only
    allow_headers=["*"],
)

# Include routes
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Health check."""
    return {"status": "healthy"}
