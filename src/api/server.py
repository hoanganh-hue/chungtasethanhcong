"""
FastAPI Server for OpenManus-Youtu Integrated Framework

This module provides the main FastAPI application and server configuration.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import time
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from .routes import router
from .unified_gemini_api import router as gemini_router
from .simple_endpoints import router as simple_router
from .models import ErrorResponse
from ..utils.logging_config import setup_logging
from ..utils.environment_manager import EnvironmentManager

# Setup logging
logger = setup_logging(__name__)

# Global app instance
app_instance: FastAPI = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting OpenManus-Youtu Integrated Framework API Server")
    
    # Initialize environment manager
    env_manager = EnvironmentManager()
    await env_manager.initialize()
    
    # Register startup event
    app.state.env_manager = env_manager
    app.state.start_time = time.time()
    
    logger.info("API Server startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OpenManus-Youtu Integrated Framework API Server")
    
    # Cleanup environment manager
    if hasattr(app.state, 'env_manager'):
        await app.state.env_manager.cleanup()
    
    logger.info("API Server shutdown completed")


def create_app(
    title: str = "OpenManus-Youtu Integrated Framework",
    description: str = "Unified AI Agent Framework combining OpenManus and Youtu-Agent capabilities",
    version: str = "1.0.0",
    debug: bool = False,
    cors_origins: list = None,
    trusted_hosts: list = None
) -> FastAPI:
    """Create and configure FastAPI application."""
    
    global app_instance
    
    # Default CORS origins
    if cors_origins is None:
        cors_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ]
    
    # Default trusted hosts
    if trusted_hosts is None:
        trusted_hosts = ["localhost", "127.0.0.1"]
    
    # Create FastAPI app
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        debug=debug,
        lifespan=lifespan,
        docs_url="/docs" if debug else None,
        redoc_url="/redoc" if debug else None,
        openapi_url="/openapi.json" if debug else None
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )
    
    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    # Add exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                detail=str(exc) if debug else "An unexpected error occurred",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            ).dict()
        )
    
    # Include API routes
    app.include_router(router, prefix="/api/v1", tags=["API"])
    
    # Include Gemini API routes
    app.include_router(gemini_router, prefix="/api/v1", tags=["Gemini AI"])
    
    # Include Simple endpoints
    app.include_router(simple_router, tags=["System"])
    
    # Add root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "OpenManus-Youtu Integrated Framework API",
            "version": version,
            "status": "running",
            "docs": "/docs" if debug else "Documentation not available in production"
        }
    
    # Add custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=title,
            version=version,
            description=description,
            routes=app.routes,
        )
        
        # Add custom info
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        
        # Add servers
        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.openmanus-youtu.com",
                "description": "Production server"
            }
        ]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    # Store app instance
    app_instance = app
    
    return app


def get_app() -> FastAPI:
    """Get the global app instance."""
    if app_instance is None:
        raise RuntimeError("App not initialized. Call create_app() first.")
    return app_instance


# Health check endpoint for load balancers
@app_instance.get("/health") if app_instance else None
async def health_check():
    """Simple health check for load balancers."""
    return {"status": "healthy", "timestamp": time.time()}


# Metrics endpoint
@app_instance.get("/metrics") if app_instance else None
async def metrics():
    """Basic metrics endpoint."""
    if not app_instance:
        return {"error": "App not initialized"}
    
    uptime = time.time() - getattr(app_instance.state, 'start_time', time.time())
    
    return {
        "uptime": uptime,
        "version": "1.0.0",
        "status": "running",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    
    # Create app
    app = create_app(debug=True)
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )