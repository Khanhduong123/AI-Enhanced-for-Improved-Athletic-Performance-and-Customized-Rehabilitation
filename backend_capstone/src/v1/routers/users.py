from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from ..models.user import User, UserCreate, UserUpdate
from ..services.user_service import create_user, get_user, update_user, authenticate_user, delete_user, get_all_patients

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """
    Register a new user (patient or doctor)
    """
    return await create_user(user)

@router.post("/login")
async def login(email: str, password: str):
    """
    Authenticate a user and return basic user information
    """
    user = await authenticate_user(email, password)
    response = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }
    
    # Add specialization for doctors
    if user.specialization and (user.role.lower() == "doctor" or user.role.lower() == "docter"):
        response["specialization"] = user.specialization
        
    # Add diagnosis for patients
    if user.diagnosis and (user.role.lower() == "patient"):
        response["diagnosis"] = user.diagnosis
        
    return response

@router.get("/patients", response_model=List[User])
async def list_all_patients():
    """
    Get a list of all registered patients.
    """
    return await get_all_patients()

@router.get("/{user_id}", response_model=User)
async def get_user_by_id(user_id: str):
    """
    Get user information by ID
    """
    return await get_user(user_id)

@router.put("/{user_id}", response_model=User)
async def update_user_info(user_id: str, user_update: UserUpdate):
    """
    Update user information
    """
    return await update_user(user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(user_id: str):
    """
    Delete a user by ID
    """
    await delete_user(user_id)
    return None 