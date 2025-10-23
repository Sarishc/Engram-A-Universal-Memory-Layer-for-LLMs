"""FastAPI server application."""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from engram.api.middleware import AuthMiddleware, RequestLoggingMiddleware
from engram.api.models import HealthResponse
from engram.api.routes import router
from engram.api.ingest_routes import router as ingest_router
from engram.api.graph_routes import router as graph_router
from engram.api.chat_routes import router as chat_router
from engram.api.router_routes import router as router_router
from engram.api.processing_routes import router as processing_router
from engram.api.analytics_routes import router as analytics_router
from engram.api.connector_routes import router as connector_router
from engram.api.memory_routes import router as memory_router
from engram.utils.config import get_settings
from engram.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Track application start time
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Engram API server")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Vector backend: {settings.vector_backend}")
    logger.info(f"Embeddings provider: {settings.default_embeddings_provider}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Engram API server")


# Create FastAPI application
app = FastAPI(
    title="Engram - Universal Memory Layer for LLMs",
    description="A provider-agnostic semantic memory service for LLM applications",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(AuthMiddleware, require_auth=True)
app.add_middleware(RequestLoggingMiddleware)

# Include API routes
app.include_router(router, prefix=settings.api_v1_str)
app.include_router(ingest_router, prefix=settings.api_v1_str)
app.include_router(graph_router, prefix=settings.api_v1_str)
app.include_router(chat_router, prefix=settings.api_v1_str)
app.include_router(router_router, prefix=settings.api_v1_str)
app.include_router(processing_router, prefix=settings.api_v1_str)
app.include_router(analytics_router, prefix=settings.api_v1_str)
app.include_router(connector_router, prefix=settings.api_v1_str)
app.include_router(memory_router, prefix=settings.api_v1_str)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "service": "Engram",
        "description": "Universal Memory Layer for Multi-Provider LLMs",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/v1/health",
    }


@app.get("/v1/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="ok",
        uptime_seconds=uptime,
        version="0.1.0",
        timestamp=time.time(),
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "error_code": "NOT_FOUND",
            "path": str(request.url.path),
            "timestamp": time.time(),
        }
    )


@app.exception_handler(422)
async def validation_error_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "details": exc.errors() if hasattr(exc, 'errors') else str(exc),
            "timestamp": time.time(),
        }
    )


def main():
    """Main entry point for running the server."""
    import uvicorn
    
    uvicorn.run(
        "engram.api.server:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
