from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from ..models.exercise import Exercise, ExerciseCreate, ExerciseInDB, ExerciseUpdate
from ..models.user import User
from ..configs.database import MongoDB
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING, IndexModel, ASCENDING

from .user_service import get_user as get_user_from_service

COLLECTION_NAME = "exercises"

# Define MongoDB indexes for optimization (Optional but recommended)
INDEXES = [
    IndexModel([("assigned_by", ASCENDING)], background=True),
    IndexModel([("assigned_to", ASCENDING)], background=True),
    IndexModel([("status", ASCENDING)], background=True),
    IndexModel([("assigned_date", ASCENDING)], background=True),
    IndexModel([("assigned_to", ASCENDING), ("assigned_date", DESCENDING)], background=True)
]

async def ensure_indexes():
    """
    Ensure all required indexes exist in the MongoDB collection
    This function should be called during application startup
    """
    collection = MongoDB.get_collection(COLLECTION_NAME)
    await collection.create_indexes(INDEXES)

async def create_exercise(exercise: ExerciseCreate) -> Exercise:
    """Create a new exercise assignment"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    try:
        assigner = await get_user_from_service(exercise.assigned_by)
        print(f"DEBUG EXERCISE SERVICE: Assigner ID: {exercise.assigned_by}")
        print(f"DEBUG EXERCISE SERVICE: Assigner Object from get_user: {assigner}") 
        print(f"DEBUG EXERCISE SERVICE: Assigner Role: '{assigner.role}'") 
        print(f"DEBUG EXERCISE SERVICE: Assigner Role Lower: '{assigner.role.lower()}'") 
        if assigner.role.lower() not in ["doctor", "docter"]:
            print("DEBUG EXERCISE SERVICE: Assigner Role Check FAILED")
            raise HTTPException(status_code=400, detail="Assigner must be a Doctor")
        assignee = await get_user_from_service(exercise.assigned_to)
        print(f"DEBUG EXERCISE SERVICE: Assignee ID: {exercise.assigned_to}")
        print(f"DEBUG EXERCISE SERVICE: Assignee Object from get_user: {assignee}")
        print(f"DEBUG EXERCISE SERVICE: Assignee Role: '{assignee.role}'")
        print(f"DEBUG EXERCISE SERVICE: Assignee Role Lower: '{assignee.role.lower()}'")
        if assignee.role.lower() not in ["patient", "patinet"]:
            print("DEBUG EXERCISE SERVICE: Assignee Role Check FAILED") 
            raise HTTPException(status_code=400, detail="Assignee must be a Patient")
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Assigner or Assignee user not found: {e.detail}")
        else:
            raise HTTPException(status_code=400, detail=f"Invalid assigner ({exercise.assigned_by}) or assignee ({exercise.assigned_to}) ID or role: {e.detail}")
    except AttributeError:
        raise HTTPException(status_code=500, detail="Error accessing user role information")

    # Create exercise in database format
    exercise_in_db = ExerciseInDB(**exercise.dict())
    
    # Insert exercise into database
    result = await collection.insert_one(exercise_in_db.dict(by_alias=True))
    
    # Get the created exercise
    created_exercise = await collection.find_one({"_id": result.inserted_id})
    
    return Exercise(**created_exercise)

async def get_exercise(exercise_id: str) -> Exercise:
    """Get an exercise by ID (handles string and ObjectId)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    # 1. Thử tìm bằng string ID
    print(f"DEBUG EXERCISE: Searching with string ID: '{exercise_id}'")
    exercise = await collection.find_one({"_id": exercise_id})
    if exercise:
        print("DEBUG EXERCISE: Found by string ID")
        return Exercise(**exercise)

    # 2. Thử tìm bằng ObjectId nếu hợp lệ
    if ObjectId.is_valid(exercise_id):
        print(f"DEBUG EXERCISE: String ID not found, trying ObjectId: {exercise_id}")
        try:
            obj_id = ObjectId(exercise_id)
            exercise = await collection.find_one({"_id": obj_id})
            if exercise:
                print("DEBUG EXERCISE: Found by ObjectId")
                return Exercise(**exercise)
        except Exception as e:
            print(f"DEBUG EXERCISE: Error searching with ObjectId: {str(e)}")

    # Không tìm thấy
    print(f"DEBUG EXERCISE: Not found with ID: {exercise_id}")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Exercise not found"
    )

async def update_exercise(exercise_id: str, exercise_update: ExerciseUpdate) -> Exercise:
    """Update an exercise (handles string and ObjectId)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    # Remove None values
    update_data = {k: v for k, v in exercise_update.dict(exclude_unset=True).items() if v is not None}
    
    # Add updated_at timestamp
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
    else:
        return await get_exercise(exercise_id)

    # Xây dựng query filter
    filter_query = {"_id": exercise_id}
    if ObjectId.is_valid(exercise_id):
        filter_query = {"$or": [{"_id": exercise_id}, {"_id": ObjectId(exercise_id)}]}

    print(f"DEBUG EXERCISE: Update filter query: {filter_query}")

    # Update the exercise
    result = await collection.update_one(filter_query, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found to update"
        )

    # Get the updated exercise using the corrected get_exercise function
    return await get_exercise(exercise_id)

async def delete_exercise(exercise_id: str) -> None:
    """Delete an exercise by ID (handles string and ObjectId)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    # Xây dựng query filter
    filter_query = {"_id": exercise_id}
    if ObjectId.is_valid(exercise_id):
        filter_query = {"$or": [{"_id": exercise_id}, {"_id": ObjectId(exercise_id)}]}

    print(f"DEBUG EXERCISE: Delete filter query: {filter_query}")

    # Delete the exercise
    result = await collection.delete_one(filter_query)

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found to delete"
        )

async def get_patient_exercises(patient_id: str) -> List[Exercise]:
    """Get all exercises assigned to a patient (handles string/ObjectId ID)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    exercises = []
    
    # Xây dựng query filter cho patient_id
    filter_query = {"assigned_to": patient_id}
    if ObjectId.is_valid(patient_id):
        filter_query = {"$or": [{"assigned_to": patient_id}, {"assigned_to": ObjectId(patient_id)}]}

    print(f"DEBUG EXERCISE: Get patient exercises filter: {filter_query}")
    cursor = collection.find(filter_query).sort("assigned_date", DESCENDING)
    
    async for exercise in cursor:
        exercises.append(Exercise(**exercise))
    
    return exercises

async def get_doctor_assigned_exercises(doctor_id: str) -> List[Exercise]:
    """Get all exercises assigned by a doctor (handles string/ObjectId ID)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    exercises = []
    
    # Xây dựng query filter cho doctor_id
    filter_query = {"assigned_by": doctor_id}
    if ObjectId.is_valid(doctor_id):
        filter_query = {"$or": [{"assigned_by": doctor_id}, {"assigned_by": ObjectId(doctor_id)}]}

    print(f"DEBUG EXERCISE: Get doctor exercises filter: {filter_query}")
    cursor = collection.find(filter_query).sort("assigned_date", DESCENDING)
    
    async for exercise in cursor:
        exercises.append(Exercise(**exercise))
    
    return exercises

async def update_exercise_status(exercise_id: str, status: str) -> Exercise:
    """Update the status of an exercise (handles string/ObjectId ID)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    # Xây dựng query filter
    filter_query = {"_id": exercise_id}
    if ObjectId.is_valid(exercise_id):
        filter_query = {"$or": [{"_id": exercise_id}, {"_id": ObjectId(exercise_id)}]}

    print(f"DEBUG EXERCISE: Update status filter query: {filter_query}")

    # Update the exercise status
    result = await collection.update_one(
        filter_query,
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )

    if result.matched_count == 0:
        try:
            await get_exercise(exercise_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise not found to update status"
            )
        except HTTPException as e:
            if e.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Exercise not found to update status"
                )
            else: raise e

    # Get the updated exercise using the corrected get_exercise function
    return await get_exercise(exercise_id) 