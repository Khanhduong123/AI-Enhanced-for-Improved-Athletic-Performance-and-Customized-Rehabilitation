from fastapi import APIRouter

router = APIRouter(prefix="/inference_video_v1", tags=["Inference from video "])

@router.post("/predict")
async def predict():
    return {"message": "Hello, World!"}