from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum
from .user import PyObjectId
from bson import ObjectId

class PredictionStatus(str, Enum):
    """Enum for prediction status"""
    COMPLETED = "Completed"
    NOT_COMPLETED = "Not Completed"
    PENDING = "Pending"
    FAILED = "Failed"

class PredictionBase(BaseModel):
    """Base model for prediction data"""
    video_id: PyObjectId = Field(..., description="ID of the video that was analyzed")
    exercise_id: PyObjectId = Field(..., description="ID of the exercise being performed")
    patient_id: PyObjectId = Field(..., description="ID of the patient who performed the exercise")
    predicted_motion: str = Field(..., description="The motion predicted by the AI model")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score of the prediction (0-1)")
    model_name: str = Field(..., description="Name of the AI model used for prediction")
    
class PredictionCreate(PredictionBase):
    """Model for creating a new prediction"""
    pass

class PredictionInDB(PredictionBase):
    """Model for storing prediction in the database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    is_match: bool = Field(..., description="Whether the prediction matches the expected exercise")
    status: PredictionStatus = Field(default=PredictionStatus.PENDING, description="Current status of the prediction")
    raw_results: Dict[str, Any] = Field(default_factory=dict, description="Raw results from the AI model")
    feedback: Optional[str] = Field(None, description="Optional feedback from the doctor")
    feedback_date: Optional[datetime] = Field(None, description="Timestamp when feedback was provided")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator("status", pre=True)
    def set_status_from_is_match(cls, v, values):
        """Set status based on is_match if status is not provided"""
        if v == PredictionStatus.PENDING and "is_match" in values:
            return PredictionStatus.COMPLETED if values["is_match"] else PredictionStatus.NOT_COMPLETED
        return v
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "video_id": "507f1f77bcf86cd799439011",
                "exercise_id": "507f1f77bcf86cd799439012",
                "patient_id": "507f1f77bcf86cd799439013",
                "predicted_motion": "Squat",
                "confidence_score": 0.95,
                "model_name": "MoveNet_Thunder",
                "is_match": True,
                "status": "Completed",
                "raw_results": {"class": "Squat", "confidence": 0.95, "features": []}
            }
        }

class Prediction(PredictionBase):
    """Model for prediction returned to the client"""
    id: PyObjectId = Field(..., alias="_id")
    is_match: bool
    status: PredictionStatus
    raw_results: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    feedback_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class PredictionUpdate(BaseModel):
    """Model for updating a prediction"""
    feedback: Optional[str] = None
    status: Optional[PredictionStatus] = None
    
    class Config:
        json_encoders = {ObjectId: str} 