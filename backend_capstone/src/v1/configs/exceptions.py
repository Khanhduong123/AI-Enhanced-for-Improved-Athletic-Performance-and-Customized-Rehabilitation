import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Exception raised when database connection fails"""
    pass

class DatabaseOperationError(Exception):
    """Exception raised when database operation fails"""
    pass

class ResourceNotFoundError(Exception):
    """Exception raised when requested resource is not found"""
    pass

class AuthenticationError(Exception):
    """Exception raised when authentication fails"""
    pass

class AuthorizationError(Exception):
    """Exception raised when user is not authorized to perform an action"""
    pass

class VideoProcessingError(Exception):
    """Exception raised when video processing fails"""
    pass

class PredictionError(Exception):
    """Exception raised when prediction fails"""
    pass

def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers for the application"""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "Validation error", "details": exc.errors()},
        )
    
    @app.exception_handler(PyMongoError)
    async def mongodb_exception_handler(request: Request, exc: PyMongoError):
        logger.error(f"MongoDB error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Database error", "details": str(exc)},
        )
    
    @app.exception_handler(ServerSelectionTimeoutError)
    async def mongodb_connection_exception_handler(request: Request, exc: ServerSelectionTimeoutError):
        logger.error(f"MongoDB connection error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "Database connection error", "details": "Unable to connect to the database"},
        )
    
    @app.exception_handler(DatabaseConnectionError)
    async def database_connection_exception_handler(request: Request, exc: DatabaseConnectionError):
        logger.error(f"Database connection error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "Database connection error", "details": str(exc)},
        )
    
    @app.exception_handler(DatabaseOperationError)
    async def database_operation_exception_handler(request: Request, exc: DatabaseOperationError):
        logger.error(f"Database operation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Database operation error", "details": str(exc)},
        )
    
    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundError):
        logger.warning(f"Resource not found: {exc}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Resource not found", "details": str(exc)},
        )
    
    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError):
        logger.warning(f"Authentication error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Authentication error", "details": str(exc)},
        )
    
    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, exc: AuthorizationError):
        logger.warning(f"Authorization error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "Authorization error", "details": str(exc)},
        )
    
    @app.exception_handler(VideoProcessingError)
    async def video_processing_exception_handler(request: Request, exc: VideoProcessingError):
        logger.error(f"Video processing error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Video processing error", "details": str(exc)},
        )
    
    @app.exception_handler(PredictionError)
    async def prediction_exception_handler(request: Request, exc: PredictionError):
        logger.error(f"Prediction error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Prediction error", "details": str(exc)},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error"},
        )
    
    logger.info("Exception handlers configured") 