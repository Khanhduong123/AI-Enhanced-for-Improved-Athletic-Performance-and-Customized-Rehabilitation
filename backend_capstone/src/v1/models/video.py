from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .user import PyObjectId
from bson import ObjectId

class VideoBase(BaseModel):
    patient_id: PyObjectId = Field(..., description="Patient ID who uploaded this video")
    exercise_id: PyObjectId = Field(..., description="Exercise ID this video is for")
    file_path: str = Field(..., description="Path to the stored video file")
    file_name: str
    file_size: int = Field(..., description="Size in bytes")
    content_type: str = Field(..., description="MIME type of the video")
    
class VideoCreate(VideoBase):
    pass
    
class VideoInDB(VideoBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="Uploaded", description="Uploaded, Processed, Failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        
class Video(VideoBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    upload_date: datetime
    status: str
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        
class VideoUpdate(BaseModel):
    status: Optional[str] = None
    
    class Config:
        json_encoders = {ObjectId: str} 