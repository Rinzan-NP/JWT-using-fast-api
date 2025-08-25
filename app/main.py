"""
FastAPI application entry point.
Similar to Django's wsgi.py but also includes URL configuration.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="FastAPI JWT Authentication System"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "FastAPI JWT Authentication API"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}