from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from ..models.prediction import Prediction, PredictionCreate, PredictionInDB, PredictionStatus, PredictionUpdate
from ..configs.database import MongoDB
from bson import ObjectId
from datetime import datetime
from .exercise_service import get_exercise, update_exercise_status
from pymongo import DESCENDING, IndexModel, ASCENDING
from ..ai.model_providers import ModelProvider
from ..ai.model_service import predict_action

COLLECTION_NAME = "predictions"

# Define MongoDB indexes for optimization
INDEXES = [
    IndexModel([("patient_id", ASCENDING)], background=True),
    IndexModel([("exercise_id", ASCENDING)], background=True),
    IndexModel([("video_id", ASCENDING)], unique=True, background=True),
    IndexModel([("created_at", DESCENDING)], background=True),
    IndexModel([("patient_id", ASCENDING), ("created_at", DESCENDING)], background=True),
    IndexModel([("exercise_id", ASCENDING), ("created_at", DESCENDING)], background=True),
    IndexModel([("status", ASCENDING), ("created_at", DESCENDING)], background=True)
]

async def ensure_indexes():
    """
    Ensure all required indexes exist in the MongoDB collection
    This function should be called during application startup
    """
    collection = MongoDB.get_collection(COLLECTION_NAME)
    await collection.create_indexes(INDEXES)

async def create_prediction(
    video_id: str,
    exercise_id: str,
    patient_id: str,
    predicted_motion: str,
    confidence_score: float,
    model_name: str,
    raw_results: Dict[str, Any] = {}
) -> Prediction:
    """
    Create a new prediction record and update exercise status if needed
    
    Args:
        video_id: ID of the video that was analyzed
        exercise_id: ID of the exercise being performed
        patient_id: ID of the patient who performed the exercise
        predicted_motion: The motion predicted by the AI model
        confidence_score: Confidence score of the prediction (0-1)
        model_name: Name of the AI model used for prediction
        raw_results: Raw results from the AI model
        
    Returns:
        Created Prediction object
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        collection = MongoDB.get_collection(COLLECTION_NAME)
        
        # Check if a prediction already exists for this video
        existing = await collection.find_one({"video_id": ObjectId(video_id)})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Prediction already exists for video {video_id}"
            )
        
        # Get the exercise to check if prediction matches
        exercise = await get_exercise(exercise_id)
        
        # Check if the predicted motion matches the exercise name
        is_match = predicted_motion.lower() == exercise.name.lower()
        
        # Create prediction record
        prediction_data = PredictionCreate(
            video_id=video_id,
            exercise_id=exercise_id,
            patient_id=patient_id,
            predicted_motion=predicted_motion,
            confidence_score=confidence_score,
            model_name=model_name
        )
        
        # Set status based on the match
        status_value = PredictionStatus.COMPLETED if is_match else PredictionStatus.NOT_COMPLETED
        
        prediction_in_db = PredictionInDB(
            **prediction_data.dict(),
            is_match=is_match,
            status=status_value,
            raw_results=raw_results,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Insert into database
        result = await collection.insert_one(prediction_in_db.dict(by_alias=True))
        
        # Update exercise status based on prediction
        await update_exercise_status(exercise_id, status_value.value)
        
        # Get the created prediction
        created_prediction = await collection.find_one({"_id": result.inserted_id})
        
        return Prediction(**created_prediction)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prediction: {str(e)}"
        )

async def get_prediction(prediction_id: str) -> Prediction:
    """
    Get a prediction by ID
    
    Args:
        prediction_id: The unique identifier of the prediction
        
    Returns:
        Prediction object
        
    Raises:
        HTTPException: If prediction not found or database operation fails
    """
    try:
        collection = MongoDB.get_collection(COLLECTION_NAME)
        prediction = await collection.find_one({"_id": ObjectId(prediction_id)})
        
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prediction with ID {prediction_id} not found"
            )
        
        return Prediction(**prediction)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prediction: {str(e)}"
        )

async def get_video_prediction(video_id: str) -> Optional[Prediction]:
    """
    Get the prediction for a specific video
    
    Args:
        video_id: The unique identifier of the video
        
    Returns:
        Prediction object or None if no prediction exists
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        collection = MongoDB.get_collection(COLLECTION_NAME)
        prediction = await collection.find_one({"video_id": ObjectId(video_id)})
        
        if not prediction:
            return None
        
        return Prediction(**prediction)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get video prediction: {str(e)}"
        )

async def get_exercise_predictions(
    exercise_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    confidence_threshold: Optional[float] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Prediction]:
    """
    Get all predictions for a specific exercise with filtering and pagination
    
    Args:
        exercise_id: The unique identifier of the exercise
        start_date: Filter for predictions after this date
        end_date: Filter for predictions before this date
        confidence_threshold: Filter for predictions with confidence score >= threshold
        status: Filter for predictions with specific status
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of prediction objects
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        collection = MongoDB.get_collection(COLLECTION_NAME)
        
        # Build query with filters
        query = {"exercise_id": ObjectId(exercise_id)}
        
        if start_date:
            query["created_at"] = {"$gte": start_date}
        if end_date:
            query.setdefault("created_at", {}).update({"$lte": end_date})
        if confidence_threshold is not None:
            query["confidence_score"] = {"$gte": confidence_threshold}
        if status:
            query["status"] = status
        
        # Execute query with pagination
        cursor = collection.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
        
        predictions = []
        async for prediction in cursor:
            predictions.append(Prediction(**prediction))
        
        return predictions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get exercise predictions: {str(e)}"
        )

async def get_patient_predictions(
    patient_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Prediction]:
    """
    Get all predictions for a specific patient with filtering and pagination
    
    Args:
        patient_id: The unique identifier of the patient
        start_date: Filter for predictions after this date
        end_date: Filter for predictions before this date
        status: Filter for predictions with specific status
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of prediction objects
        
    Raises:
        HTTPException: If database operation fails
    """
    try:
        collection = MongoDB.get_collection(COLLECTION_NAME)
        
        # Build query with filters
        query = {"patient_id": ObjectId(patient_id)}
        
        if start_date:
            query["created_at"] = {"$gte": start_date}
        if end_date:
            query.setdefault("created_at", {}).update({"$lte": end_date})
        if status:
            query["status"] = status
        
        # Execute query with pagination
        cursor = collection.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
        
        predictions = []
        async for prediction in cursor:
            predictions.append(Prediction(**prediction))
        
        return predictions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient predictions: {str(e)}"
        )

async def update_prediction_feedback(
    prediction_id: str,
    feedback: str,
    doctor_id: str
) -> Prediction:
    """
    Update a prediction with doctor's feedback
    
    Args:
        prediction_id: The unique identifier of the prediction
        feedback: The feedback text from the doctor
        doctor_id: ID of the doctor providing feedback
        
    Returns:
        Updated prediction object
        
    Raises:
        HTTPException: If prediction not found or update fails
    """
    try:
        collection = MongoDB.get_collection(COLLECTION_NAME)
        
        # Verify prediction exists
        prediction = await get_prediction(prediction_id)
        
        # Update with feedback
        update_data = {
            "$set": {
                "feedback": feedback,
                "feedback_date": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
        
        result = await collection.update_one(
            {"_id": ObjectId(prediction_id)},
            update_data
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED,
                detail="Prediction not updated"
            )
        
        # Get updated prediction
        updated_prediction = await get_prediction(prediction_id)
        return updated_prediction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update prediction feedback: {str(e)}"
        )

async def analyze_video(
    video_path: str,
    exercise_id: str,
    patient_id: str,
    video_id: str
) -> Prediction:
    """
    Analyze a video using the AI model and create a prediction
    
    Args:
        video_path: Path to the video file
        exercise_id: ID of the exercise being performed
        patient_id: ID of the patient who performed the exercise
        video_id: ID of the video record
        
    Returns:
        Prediction object with analysis results
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Load model from the provider
        model = ModelProvider.get_model()
        model_name = ModelProvider.get_model_name()
        classes = ModelProvider.get_classes()
        
        # Run inference
        prediction_result = predict_action(video_path, model, model_name, classes)
        
        # Extract predicted motion and confidence
        predicted_motion = prediction_result["class"]
        confidence_score = prediction_result["confidence"]
        
        # Create prediction record
        prediction = await create_prediction(
            video_id=video_id,
            exercise_id=exercise_id,
            patient_id=patient_id,
            predicted_motion=predicted_motion,
            confidence_score=confidence_score,
            model_name=model_name,
            raw_results=prediction_result
        )
        
        return prediction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze video: {str(e)}"
        ) 