from fastapi import APIRouter
from .v1.routers.predict import router as PredictionUploadVideoRouter
# from .v1.routers.health import router as HealthCheckRouter
from .v1.routers.users import router as UsersRouter
from .v1.routers.exercises import router as ExercisesRouter
from .v1.routers.videos import router as VideosRouter
from .v1.routers.predictions import router as PredictionsRouter

# Create the APIRouter
api_v1_router = APIRouter(prefix="/v1")

# Include the routers
api_v1_router.include_router(PredictionUploadVideoRouter)
# api_v1_router.include_router(HealthCheckRouter)
api_v1_router.include_router(UsersRouter)
api_v1_router.include_router(ExercisesRouter)
api_v1_router.include_router(VideosRouter)
api_v1_router.include_router(PredictionsRouter)