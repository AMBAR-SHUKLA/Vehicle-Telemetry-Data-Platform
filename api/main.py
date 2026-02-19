"""
Vehicle Telemetry Data Platform - Main API Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from database.models import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info("Starting Vehicle Telemetry Platform API...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down Vehicle Telemetry Platform API...")


# Create FastAPI application
app = FastAPI(
    title="Vehicle Telemetry Data Platform",
    description="""
    A high-performance platform for processing vehicle telemetry data and 
    optimizing fleet routing using advanced graph algorithms.
    
    ## Features
    
    * **Vehicle Management**: Register and track vehicles in your fleet
    * **Telemetry Ingestion**: Real-time vehicle data processing
    * **Route Optimization**: Advanced algorithms for optimal routing
    * **Performance**: Parallel computation with C++ engine
    
    ## Tech Stack
    
    * FastAPI + Python 3.11+
    * C++17 with OpenMP
    * PostgreSQL/SQLite
    * Docker + GitHub Actions
    """,
    version="1.0.0",
    contact={
        "name": "Ambar Shukla",
        "url": "https://github.com/AMBAR-SHUKLA",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Vehicle Telemetry Data Platform API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": "/docs",
        "github": "https://github.com/AMBAR-SHUKLA/Vehicle-Telemetry-Data-Platform"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "database": "connected",
            "engine": "ready"
        }
    }


# Import and include routers
from api.routers import vehicles, telemetry
app.include_router(vehicles.router)
app.include_router(telemetry.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
