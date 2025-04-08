from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from ..models.user import User, UserCreate, UserUpdate
from ..services.user_service import create_user, get_user, update_user, authenticate_user, delete_user

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
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role
    }

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