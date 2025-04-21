import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from .v1.configs.swagger import swagger_config
from .v1.configs.database import MongoDB
from .v1.configs.middleware import setup_middlewares
from .v1.configs.exceptions import setup_exception_handlers
from .v1.configs.logging_config import setup_logging
from .v1.configs.app_config import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for the FastAPI application
    """
    # Setup logging
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.ENVIRONMENT} mode")
    
    # Connect to database on startup
    logger.info("Connecting to MongoDB...")
    await MongoDB.connect_to_mongo()
    
    # Yield control to the application
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down application...")
    await MongoDB.close_mongo_connection()

# Define create_app function.
# Avoid circular import by using this function
# to create FastAPI app instance.
def create_app():
    # Create a custom swagger config with our settings
    custom_swagger = swagger_config.copy()
    custom_swagger["title"] = settings.APP_NAME
    custom_swagger["description"] = "API for exercise tracking and analysis using AI"
    custom_swagger["version"] = settings.APP_VERSION
    
    app = FastAPI(
        **custom_swagger,
        lifespan=lifespan,
        debug=settings.DEBUG
    )
    
    # Setup middleware (CORS, logging, etc.)
    setup_middlewares(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    app.mount("/uploaded_videos", StaticFiles(directory="uploaded_videos"), name="uploaded_videos")
    # Add healthcheck endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for Kubernetes/monitoring"""
        return {"status": "healthy", "version": settings.APP_VERSION}
    
    return app