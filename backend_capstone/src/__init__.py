from fastapi import APIRouter
from .v1.routers.predict import router as PredictionUploadVideoRouter
# from .v1.routers.health import router as HealthCheckRouter
from .v1.routers.skeleton import router as SkeletonExtractionRouter

# Create the APIRouter
api_v1_router = APIRouter(prefix="/v1")

# Include the routers
api_v1_router.include_router(PredictionUploadVideoRouter)
# api_v1_router.include_router(HealthCheckRouter)
api_v1_router.include_router(SkeletonExtractionRouter)