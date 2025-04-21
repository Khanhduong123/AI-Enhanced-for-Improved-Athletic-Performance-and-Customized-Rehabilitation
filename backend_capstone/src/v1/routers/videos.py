from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from ..models.video import Video, VideoUpdate
from ..services.video_service import get_video, get_patient_videos, update_video_status, delete_video
from ..services.prediction_service import get_video_prediction

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.get("/{video_id}", response_model=Dict[str, Any])
async def get_video_with_prediction(video_id: str):
    """
    Get a video by ID with its prediction if available
    """
    video = await get_video(video_id)
    prediction = await get_video_prediction(video_id)
    
    return {
        "video": {
            "id": str(video.id),
            "file_name": video.file_name,
            "upload_date": video.upload_date,
            "status": video.status
        },
        "prediction": {
            "predicted_motion": prediction.predicted_motion if prediction else None,
            "confidence_score": prediction.confidence_score if prediction else None,
            "is_match": prediction.is_match if prediction else None,
            "created_at": prediction.created_at if prediction else None
        }
    }

@router.put("/{video_id}", response_model=Video)
async def update_video(video_id: str, video_update: VideoUpdate):
    """
    Update a video's status
    """
    return await update_video_status(video_id, video_update.status)

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_video(video_id: str):
    """
    Delete a video by ID
    """
    await delete_video(video_id)
    return None

@router.get("/patient/{patient_id}", response_model=List[Dict[str, Any]])
async def get_videos_by_patient(patient_id: str):
    """
    Get all videos uploaded by a patient with their predictions
    """
    videos = await get_patient_videos(patient_id)
    result = []
    
    for video in videos:
        prediction = await get_video_prediction(str(video.id))
        result.append({
            "video": {
                "id": str(video.id),
                "file_name": video.file_name,
                "upload_date": video.upload_date,
                "status": video.status
            },
            "prediction": {
                "predicted_motion": prediction.predicted_motion if prediction else None,
                "confidence_score": prediction.confidence_score if prediction else None,
                "is_match": prediction.is_match if prediction else None,
                "created_at": prediction.created_at if prediction else None
            }
        })
    
    return result 