import time
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from .app_config import settings

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request information and timing"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.debug(f"Request: {request.method} {request.url.path}")
        
        # Process the request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response time
            logger.debug(f"Response: {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Error processing request: {request.method} {request.url.path} - {str(e)} - {process_time:.4f}s")
            raise

def setup_middlewares(app: FastAPI):
    """Setup all middlewares for the application"""
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Setup rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    logger.info("Middlewares configured") 