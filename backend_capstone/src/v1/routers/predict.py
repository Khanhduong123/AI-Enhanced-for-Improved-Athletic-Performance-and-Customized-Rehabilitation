import os
import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from ..providers.model_providers import ModelProvider
from ..services.model_service import predict_action

# Create the APIRouter
router = APIRouter(prefix="/predict", tags=["Prediction Upload Video"])

@router.post("/", response_model=Dict[str, Any])
async def predict_pose(video_file: UploadFile = File(...)):
    """
    Receive a video file, run inference, and return the predicted pose.
    
    Parameters:
    - video_file: The uploaded video file (must be in MP4 format, max 50MB)
    
    Returns:
    - Dictionary containing the prediction result
    
    Raises:
    - HTTPException: If file validation fails or prediction encounters an error
    """
    # Validate file type
    if not video_file.content_type or "video" not in video_file.content_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a video"
        )
    
    # Create a unique filename
    temp_filename = f"{uuid.uuid4()}.mp4"
    temp_filepath = os.path.join("temp_videos", temp_filename)
    os.makedirs("temp_videos", exist_ok=True)

    try:
        # Save the uploaded file
        file_content = await video_file.read()
        
        # Check file size (limit to 50MB)
        if len(file_content) > 50 * 1024 * 1024:  
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 50MB limit"
            )
        
        with open(temp_filepath, "wb") as f:
            f.write(file_content)

        # Load model from the provider
        model = ModelProvider.get_model()
        model_name = ModelProvider.get_model_name()
        classes = ModelProvider.get_classes()

        # Run inference
        prediction = predict_action(temp_filepath, model, model_name, classes)

        return {"prediction": prediction}
    
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
    finally:
        # Clean up temporary file
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception as e:
                print(f"Failed to remove temporary file: {str(e)}")