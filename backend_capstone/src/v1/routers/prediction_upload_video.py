import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..providers.model_providers import ModelProvider
from ..services.model_service import predict_action

# Create the APIRouter
router = APIRouter(prefix="/prediction_upload_video", tags=["Prediction Upload Video"])

@router.post("/")
async def predict_pose(video_file: UploadFile = File(...)):
    """
    Receive a video file, run inference, and return the predicted pose.
    """
    # 1) Save the uploaded file to a temporary path
    try:
        temp_filename = f"{uuid.uuid4()}.mp4"
        temp_filepath = os.path.join("temp_videos", temp_filename)
        os.makedirs("temp_videos", exist_ok=True)

        with open(temp_filepath, "wb") as f:
            f.write(await video_file.read())

        # 2) Load model from the provider
        model = ModelProvider.get_model()
        model_name = ModelProvider.get_model_name()
        classes = ModelProvider.get_classes()

        # 3) Run inference
        prediction = predict_action(temp_filepath, model, model_name, classes)

        # 4) Clean up temporary file if desired
        os.remove(temp_filepath)

        return {"prediction": prediction}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))