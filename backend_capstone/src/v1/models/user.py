from typing import Optional, List, Annotated
from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from datetime import datetime
from bson import ObjectId

# Updated PyObjectId for Pydantic v2
def validate_object_id(v) -> str:
    if not ObjectId.is_valid(v):
        raise ValueError("Invalid ObjectId")
    return str(v)

PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = Field(..., description="Either 'Patient' or 'Doctor'")
    
class UserCreate(UserBase):
    password: str
    
class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        
class User(UserBase):
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    
    class Config:
        json_encoders = {ObjectId: str} 