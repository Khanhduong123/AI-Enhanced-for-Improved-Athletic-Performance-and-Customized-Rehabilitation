from fastapi import APIRouter
from .v1.routers.predict import router as PredictionUploadVideoRouter

# Create the APIRouter
api_v1_router = APIRouter(prefix="/v1")

# Include the routers
api_v1_router.include_router(PredictionUploadVideoRouter)