from typing import List, Optional
from fastapi import HTTPException, status
from ..models.user import User, UserCreate, UserInDB, UserUpdate
from ..configs.database import MongoDB
from bson import ObjectId
from datetime import datetime
import hashlib
from pymongo import IndexModel, ASCENDING, TEXT

COLLECTION_NAME = "users"

# Define MongoDB indexes for optimization
INDEXES = [
    IndexModel([("email", ASCENDING)], unique=True, background=True),
    IndexModel([("role", ASCENDING)], background=True),
    IndexModel([("created_at", ASCENDING)], background=True)
]

async def get_password_hash(password: str) -> str:
    """Generate a hashed password"""
    return hashlib.sha256(password.encode()).hexdigest()

async def create_user(user: UserCreate) -> User:
    """Create a new user"""
    # Check if email already exists
    collection = MongoDB.get_collection(COLLECTION_NAME)
    if await collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create a mutable dictionary from the user data
    user_data = user.dict()
    
    # Set default specialization for doctors
    if user.role.lower() == "doctor" or user.role.lower() == "docter":
        if not user_data.get("specialization"):
            user_data["specialization"] = "Physical Therapist"
    
    # Create user with hashed password
    user_in_db = UserInDB(
        **user_data,
        hashed_password=await get_password_hash(user.password)
    )
    
    # Insert user into database
    result = await collection.insert_one(user_in_db.dict(by_alias=True))
    
    # Get the created user
    created_user = await collection.find_one({"_id": result.inserted_id})
    
    return User(**created_user)

async def get_user(user_id: str):
    """Get a user by ID (handles both string and ObjectId formats)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    # 1. Ưu tiên tìm kiếm bằng ID string nguyên gốc
    print(f"DEBUG: Searching with string ID: '{user_id}'")
    user = await collection.find_one({"_id": user_id})
    if user:
        print("DEBUG: Found user by string ID")
        return User(**user)
    
    # 2. Nếu không tìm thấy bằng string và ID hợp lệ, thử tìm bằng ObjectId
    if ObjectId.is_valid(user_id):
        print(f"DEBUG: String ID not found, trying ObjectId: {user_id}")
        try:
            obj_id = ObjectId(user_id)
            user = await collection.find_one({"_id": obj_id})
            if user:
                print("DEBUG: Found user by ObjectId")
                return User(**user)
        except Exception as e:
            print(f"DEBUG: Error converting to ObjectId or searching: {str(e)}")

    # 3. Nếu vẫn không tìm thấy, báo lỗi
    print(f"DEBUG: User not found with ID: {user_id} (tried string and ObjectId)")
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )

async def get_user_by_email(email: str) -> UserInDB:
    """Get a user by email (including password hash)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    user = await collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserInDB(**user)

async def update_user(user_id: str, user_update: UserUpdate) -> User:
    """Update a user (handles both string and ObjectId IDs)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    # Remove None values
    update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items() if v is not None}
    
    # Hash password if provided
    if "password" in update_data:
        update_data["hashed_password"] = await get_password_hash(update_data.pop("password"))
    
    # Add updated_at timestamp
    update_data["updated_at"] = datetime.utcnow()
    
    # Xây dựng query để tìm kiếm cả string và ObjectId
    filter_query = {"_id": user_id}
    if ObjectId.is_valid(user_id):
        filter_query = {"$or": [{"_id": user_id}, {"_id": ObjectId(user_id)}]}

    print(f"DEBUG: Update filter query: {filter_query}")
    
    # Update the user
    result = await collection.update_one(filter_query, {"$set": update_data})
    
    if result.matched_count == 0:
         raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="User not found to update"
         )

    # Get the updated user using the corrected get_user function
    return await get_user(user_id)

async def delete_user(user_id: str) -> None:
    """Delete a user by ID (handles both string and ObjectId IDs)"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    # Xây dựng query để tìm kiếm cả string và ObjectId
    filter_query = {"_id": user_id}
    if ObjectId.is_valid(user_id):
        filter_query = {"$or": [{"_id": user_id}, {"_id": ObjectId(user_id)}]}

    print(f"DEBUG: Delete filter query: {filter_query}")
    
    # Delete the user
    result = await collection.delete_one(filter_query)
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found to delete"
        )

async def authenticate_user(email: str, password: str) -> User:
    """Authenticate a user"""
    try:
        # Lấy UserInDB để có hashed_password
        user_db = await get_user_by_email(email)
    except HTTPException:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check password
    if user_db.hashed_password != await get_password_hash(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Trả về User model (không có password)
    # Cần truy vấn lại bằng ID để lấy đúng kiểu User model
    # Vì user_db có thể có ID dạng string hoặc ObjectId
    return await get_user(user_db.id) # Sử dụng get_user đã sửa

async def ensure_indexes():
    """
    Ensure all required indexes exist in the MongoDB collection
    This function should be called during application startup
    """
    collection = MongoDB.get_collection(COLLECTION_NAME)
    await collection.create_indexes(INDEXES)

async def get_all_patients() -> List[User]:
    """Get all users with the role 'Patient'"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    patients = []
    
    # Use a simpler query that's less likely to filter incorrectly
    # Look for role that contains "patient" in any case
    cursor = collection.find({"role": {"$regex": "patient", "$options": "i"}})
    
    # Print the count for debugging
    count = await collection.count_documents({"role": {"$regex": "patient", "$options": "i"}})
    print(f"DEBUG: Found {count} patients in database")
    
    async for user_data in cursor:
        print(f"DEBUG: Processing patient with ID: {user_data.get('_id')} and role: {user_data.get('role')}")
        # Just use the user_data directly instead of calling get_user again
        try:
            patients.append(User(**user_data))
        except Exception as e:
            print(f"ERROR: Could not process patient {user_data.get('_id')}: {str(e)}")
    
    print(f"DEBUG: Returning {len(patients)} patients")
    return patients 