from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .user import PyObjectId
from bson import ObjectId
from .video import Video

class ExerciseBase(BaseModel):
    name: str
    description: str
    assigned_by: PyObjectId = Field(..., description="Doctor ID who assigned this exercise")
    assigned_to: PyObjectId = Field(..., description="Patient ID who should perform this exercise")
    assigned_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    video_id: Optional[str] = None  
    
class ExerciseCreate(ExerciseBase):
    pass
    
class ExerciseInDB(ExerciseBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    status: str = Field(default="Pending", description="Pending, Completed, Not Completed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        
class Exercise(ExerciseBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    status: str
    created_at: datetime
    updated_at: datetime
    video: Optional[Video] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        
class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    
    class Config:
        json_encoders = {ObjectId: str} 