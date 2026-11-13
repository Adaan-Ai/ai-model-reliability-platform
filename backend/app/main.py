"""
AI Model Evaluation & Data Reliability Platform
FastAPI Application Entry Point
DBMS Project - Mohammed Adaan Hamad & Navya Kishore Dash
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import (
    users_router,
    data_sources_router,
    datasets_router,
    quality_router,
    models_router,
    evaluations_router,
    drift_router,
    reliability_router,
    reports_router,
    dashboard_router,
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app with OpenAPI metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## AI Model Evaluation & Data Reliability Platform API
    
    A centralized enterprise platform that tracks machine learning models, dataset versions,
    executes real data quality checks, trains & evaluates Scikit-learn classification models,
    detects feature distribution drift (PSI & KS tests), and calculates an explainable composite reliability score.
    
    ### 12 Core Relational Entities:
    1. **USER**: Data practitioners and model owners
    2. **DATA_SOURCE**: Upstream data ingestion points
    3. **DATASET**: Logical business datasets
    4. **DATASET_VERSION**: Immutable versioned CSV snapshots
    5. **DATA_QUALITY_CHECK**: Configured data quality rules and thresholds
    6. **DATA_QUALITY_RESULT**: Deterministic quality scores and validation statuses
    7. **AI_MODEL**: Machine learning model definitions
    8. **MODEL_VERSION**: Specific algorithmic version iterations
    9. **EVALUATION_RUN**: Central operational evaluation runs
    10. **EVALUATION_RESULT**: Accuracy, Precision, Recall, and F1 scores
    11. **DRIFT_DETECTION**: Population Stability Index (PSI) distribution drift scores
    12. **RELIABILITY_SCORE**: Weighted composite reliability index and diagnostic rating
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."}
    )

# Include Domain Routers under /api
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(data_sources_router, prefix=settings.API_PREFIX)
app.include_router(datasets_router, prefix=settings.API_PREFIX)
app.include_router(quality_router, prefix=settings.API_PREFIX)
app.include_router(models_router, prefix=settings.API_PREFIX)
app.include_router(evaluations_router, prefix=settings.API_PREFIX)
app.include_router(drift_router, prefix=settings.API_PREFIX)
app.include_router(reliability_router, prefix=settings.API_PREFIX)
app.include_router(reports_router, prefix=settings.API_PREFIX)

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend service readiness."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": settings.DB_NAME
    }

@app.get("/", tags=["Root"])
def root_redirect():
    """Root redirect with basic system info."""
    return {
        "message": "Welcome to AI Model Evaluation & Data Reliability Platform API",
        "documentation": "/docs",
        "health": "/health"
    }
