from typing import List
from fastapi import APIRouter, HTTPException, status
from ..models.exercise import Exercise, ExerciseCreate, ExerciseUpdate
from ..services.exercise_service import (
    create_exercise, get_exercise, update_exercise, 
    get_patient_exercises, get_doctor_assigned_exercises, delete_exercise
)

router = APIRouter(prefix="/exercises", tags=["Exercises"])

@router.post("/", response_model=Exercise, status_code=status.HTTP_201_CREATED)
async def create_new_exercise(exercise: ExerciseCreate):
    """
    Create a new exercise assignment (doctors only)
    """
    return await create_exercise(exercise)

@router.get("/{exercise_id}", response_model=Exercise)
async def get_exercise_by_id(exercise_id: str):
    """
    Get exercise details by ID
    """
    return await get_exercise(exercise_id)

@router.put("/{exercise_id}", response_model=Exercise)
async def update_exercise_details(exercise_id: str, exercise_update: ExerciseUpdate):
    """
    Update exercise details
    """
    return await update_exercise(exercise_id, exercise_update)

@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_exercise(exercise_id: str):
    """
    Delete an exercise by ID
    """
    await delete_exercise(exercise_id)
    return None

@router.get("/patient/{patient_id}", response_model=List[Exercise])
async def get_exercises_for_patient(patient_id: str):
    """
    Get all exercises assigned to a specific patient
    """
    return await get_patient_exercises(patient_id)

@router.get("/doctor/{doctor_id}", response_model=List[Exercise])
async def get_exercises_by_doctor(doctor_id: str):
    """
    Get all exercises assigned by a specific doctor
    """
    return await get_doctor_assigned_exercises(doctor_id) 