import logging
from typing import List, Optional
from fastapi import Depends, HTTPException, status, Header
from pymongo.collection import Collection
from bson import ObjectId

from ..services.user_service import get_user
from .exceptions import AuthenticationError, AuthorizationError
from .database import MongoDB

logger = logging.getLogger(__name__)

async def get_user_from_header(x_user_id: Optional[str] = Header(None)) -> dict:
    """
    Get the user from the X-User-ID header
    
    This is a simplified auth mechanism. In production, you should use proper JWT authentication.
    """
    if not x_user_id:
        logger.warning("Missing X-User-ID header")
        raise AuthenticationError("Authentication required")
        
    try:
        user = await get_user(x_user_id)
        return user
    except Exception as e:
        logger.warning(f"User authentication failed: {str(e)}")
        raise AuthenticationError("Invalid user ID")

async def get_doctor_user(user = Depends(get_user_from_header)):
    """
    Check if the user is a doctor
    
    This dependency ensures the user has the doctor role
    """
    if user.role != "Doctor":
        logger.warning(f"Authorization failed: User {user.id} is not a doctor")
        raise AuthorizationError("Doctor access required")
    return user

async def get_patient_user(user = Depends(get_user_from_header)):
    """
    Check if the user is a patient
    
    This dependency ensures the user has the patient role
    """
    if user.role != "Patient":
        logger.warning(f"Authorization failed: User {user.id} is not a patient")
        raise AuthorizationError("Patient access required")
    return user

async def get_db_collection(collection_name: str) -> Collection:
    """
    Get a database collection
    
    This dependency provides access to the specified MongoDB collection
    """
    return MongoDB.get_collection(collection_name)

def check_object_id(id: str) -> str:
    """
    Validate that the provided ID is a valid ObjectID
    
    This utility function checks and returns the ID if valid, or raises an exception
    """
    if not ObjectId.is_valid(id):
        logger.warning(f"Invalid ObjectID format: {id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )
    return id 