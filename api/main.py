"""
SadakAI API - Main Application Entry Point

This module initializes the FastAPI application, configures middleware,
registers routers, and manages the application lifecycle including
YOLO model loading.

Author: SadakAI Team
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.config import get_settings
from api.models.database_sqlite import create_tables, engine

# Initialize settings and logger
settings = get_settings()
logger = logging.getLogger(__name__)

# Global model variable for YOLO
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown tasks:
    - Creates database tables on startup
    - Loads YOLO model into memory
    - Cleans up resources on shutdown
    
    Args:
        app: FastAPI application instance
    
    Yields:
        Control to the application
    """
    global model
    
    logger.info("Starting SadakAI API...")
    
    # Create database tables if they don't exist
    create_tables()
    logger.info("Database tables created")
    
    # Attempt to load YOLO model for hazard detection
    # This is optional - API will work without model but detection won't
    try:
        from ultralytics import YOLO
        model = YOLO(settings.MODEL_PATH)
        logger.info(f"YOLO model loaded from {settings.MODEL_PATH}")
    except Exception as e:
        logger.warning(f"Could not load YOLO model: {e}")
        logger.info("Detection endpoints will return errors until model is added")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down SadakAI API...")
    model = None


# Initialize FastAPI application with metadata
app = FastAPI(
    title="SadakAI API",
    description="Indian Road Hazard Detection & Crowdsourced Mapping Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware for frontend communication
# Allows requests from localhost during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register API routers
from api.routers import detect, hazards, stats
app.include_router(detect.router, prefix="/api", tags=["Detection"])
app.include_router(hazards.router, prefix="/api", tags=["Hazards"])
app.include_router(stats.router, prefix="/api", tags=["Stats"])


@app.get("/health", response_model=dict)
async def health_check():
    """
    Health check endpoint.
    
    Used to verify the API is running and check if the YOLO model
    has been loaded successfully.
    
    Returns:
        Dictionary with status, model_loaded flag, and version
    """
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "version": "1.0.0"
    }
