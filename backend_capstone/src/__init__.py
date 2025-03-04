from fastapi import APIRouter
from .v1.routers.inference_video import router as inference_video_v1_router


api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(inference_video_v1_router)