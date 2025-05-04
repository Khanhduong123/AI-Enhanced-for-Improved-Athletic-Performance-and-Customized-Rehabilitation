import os
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form, Path, Query, Depends
from ..ai.model_providers import ModelProvider
from ..ai.model_service import predict_action
from ..services.video_service import save_video_file, create_video_record, get_exercise_videos
from ..services.prediction_service import analyze_video, get_video_prediction, update_prediction_feedback
from ..services.exercise_service import update_exercise_status, get_exercise
from ..services.user_service import get_user
from ..models.prediction import Prediction, PredictionStatus
from ..models.video import Video
from ..core.pagination import PaginationParams, get_pagination_params
from datetime import datetime
from ..configs.app_config import settings

# Create the APIRouter
router = APIRouter(prefix="/predict", tags=["Prediction & Video Analysis"])

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def predict_pose(
    video_file: UploadFile = File(...),
    patient_id: str = Form(...),
    exercise_id: str = Form(...)
):
    """
    Upload a video file and run AI analysis to predict the motion
    
    The AI model will analyze the video and determine:
    1. The type of motion/exercise being performed
    2. How well it matches the assigned exercise
    3. The confidence score of the prediction
    
    This endpoint will:
    - Save the uploaded video file
    - Create a video record in the database
    - Run the AI model for prediction
    - Create a prediction record
    - Update the exercise status based on the prediction
    
    Parameters:
    - video_file: The uploaded video file (must be in MP4 format, max 50MB)
    - patient_id: ID of the patient uploading the video
    - exercise_id: ID of the exercise being performed
    
    Returns:
    - Dictionary containing the prediction result and video information
    
    Raises:
    - 400: Invalid patient or exercise ID
    - 413: File size exceeds limit
    - 415: Invalid file type
    - 500: Server error during processing
    """
    # Validate patient and exercise
    try:
        await get_user(patient_id)
        await get_exercise(exercise_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid patient or exercise ID: {str(e)}"
        )
    
    # Validate file type
    if not video_file.content_type or "video" not in video_file.content_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a video format"
        )
    
    # Create a unique filename
    original_filename = video_file.filename
    extension = original_filename.split(".")[-1] if "." in original_filename else "mp4"
    filename = f"{uuid.uuid4()}_{patient_id}.{extension}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    try:
        # Save the uploaded file
        file_content = await video_file.read()
        
        # Check file size (limit to 50MB)
        if len(file_content) > 50 * 1024 * 1024:  
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 50MB limit"
            )
        
        with open(filepath, "wb") as f:
            f.write(file_content)


        # Create video record in database
        video = await create_video_record(
            patient_id=patient_id,
            exercise_id=exercise_id,
            file_path=filepath,
            file_name=video_file.filename,
            file_size=len(file_content),
            content_type=video_file.content_type
        )

        # Run inference and create prediction record
        prediction_result = await analyze_video(
            video_path=filepath,
            exercise_id=exercise_id,
            patient_id=patient_id,
            video_id=str(video.id)
        )

        motion_map = {
            "Sodatvuonlen": "Sờ Đất Vươn Lên",
            "Xemxaxemgan": "Xem Xa Xem Gần",
            "Ngoithangbangtrengot": "Ngồi Thang Bằng Trên Gót",
            "Dangchanraxanghiengminh": "Đang Chân Ra Xa Nghiêng Mình"
        }
   
        # Return combined result with more detailed information
        return {
            "status": "success",
            "video": {
                "id": str(video.id),
                "filename": video.file_name,
                "upload_date": video.upload_date
            },
            "prediction": {
                "id": str(prediction_result.id),
                "predicted_motion": motion_map[prediction_result.predicted_motion],
                "confidence_score": prediction_result.confidence_score,
                "is_match": prediction_result.is_match,
                "status": prediction_result.status,
                "created_at": prediction_result.created_at
            },
            "exercise": {
                "id": exercise_id,
                "status": prediction_result.status
            }
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error (add proper logging as needed)
        print(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing video: {str(e)}"
        )


@router.get("/exercise/{exercise_id}/videos", response_model=List[Dict[str, Any]])
async def get_videos_for_exercise(
    exercise_id: str = Path(..., description="The unique identifier of the exercise"),
    start_date: Optional[datetime] = Query(None, description="Filter videos uploaded after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter videos uploaded before this date"),
    status: Optional[str] = Query(None, description="Filter by prediction status (Completed, Not Completed)"),
    pagination: PaginationParams = Depends(get_pagination_params)
):
    """
    Get all videos for a specific exercise with their predictions
    
    This endpoint retrieves all videos associated with an exercise along with their 
    prediction results. It supports filtering by date range and prediction status,
    as well as pagination.
    
    Parameters:
    - exercise_id: ID of the exercise
    - start_date: Optional filter for videos uploaded after this date
    - end_date: Optional filter for videos uploaded before this date  
    - status: Optional filter for prediction status
    - pagination: Pagination parameters (skip and limit)
    
    Returns:
    - List of dictionaries containing video and prediction information
    
    Raises:
    - 404: Exercise not found
    - 500: Server error
    """
    try:
        # Verify exercise exists
        await get_exercise(exercise_id)
        
        # Get videos with filtering
        videos = await get_exercise_videos(
            exercise_id, 
            start_date=start_date,
            end_date=end_date,
            status=status,
            skip=pagination.skip,
            limit=pagination.limit
        )
        
        result = []
        
        for video in videos:
            prediction = await get_video_prediction(str(video.id))
            result.append({
                "video": {
                    "id": str(video.id),
                    "filename": video.file_name,
                    "upload_date": video.upload_date,
                    "file_path": video.file_path,
                    "file_size": video.file_size,
                    "content_type": video.content_type
                },
                "prediction": {
                    "id": str(prediction.id) if prediction else None,
                    "predicted_motion": prediction.predicted_motion if prediction else None,
                    "is_match": prediction.is_match if prediction else None,
                    "confidence_score": prediction.confidence_score if prediction else None,
                    "status": prediction.status if prediction else None,
                    "created_at": prediction.created_at if prediction else None
                },
                "patient_id": str(video.patient_id)
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving videos: {str(e)}"
        )

@router.post("/prediction/{prediction_id}/feedback", response_model=Dict[str, Any])
async def add_feedback_to_prediction(
    prediction_id: str = Path(..., description="The unique identifier of the prediction"),
    feedback: str = Form(..., description="Feedback from the doctor"),
    doctor_id: str = Form(..., description="ID of the doctor providing feedback")
):
    """
    Add doctor's feedback to a prediction
    
    This endpoint allows doctors to provide feedback on a patient's exercise prediction.
    The feedback is stored with the prediction along with the timestamp and doctor ID.
    
    Parameters:
    - prediction_id: ID of the prediction to update
    - feedback: Feedback text from the doctor
    - doctor_id: ID of the doctor providing feedback
    
    Returns:
    - Updated prediction information
    
    Raises:
    - 400: Invalid doctor ID (must be a doctor)
    - 404: Prediction not found
    - 500: Server error
    """
    try:
        # Verify doctor
        doctor = await get_user(doctor_id)
        if doctor.role != "Doctor":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only doctors can provide feedback"
            )
        
        # Update prediction with feedback
        updated_prediction = await update_prediction_feedback(
            prediction_id=prediction_id,
            feedback=feedback,
            doctor_id=doctor_id
        )
        
        return {
            "status": "success",
            "prediction": {
                "id": str(updated_prediction.id),
                "status": updated_prediction.status,
                "feedback": updated_prediction.feedback,
                "feedback_date": updated_prediction.feedback_date
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding feedback: {str(e)}"
        )