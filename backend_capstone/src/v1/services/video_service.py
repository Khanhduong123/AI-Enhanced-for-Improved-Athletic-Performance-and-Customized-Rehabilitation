import logging
from typing import List, Optional
from fastapi import HTTPException, status, UploadFile
from ..models.video import Video, VideoCreate, VideoInDB, VideoUpdate
from ..configs.database import MongoDB
from ..configs.app_config import settings
from ..configs.exceptions import VideoProcessingError, ResourceNotFoundError, DatabaseOperationError
from bson import ObjectId
from datetime import datetime
import os
import uuid
import shutil
import aiofiles
from pymongo import DESCENDING

logger = logging.getLogger(__name__)

COLLECTION_NAME = "videos"

async def save_video_file(video_file: UploadFile, patient_id: str) -> str:
    """Save an uploaded video file to disk and return the file path"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Generate a unique filename with original extension
        original_filename = video_file.filename
        extension = original_filename.split(".")[-1] if "." in original_filename else "mp4"
        filename = f"{uuid.uuid4()}_{patient_id}.{extension}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Save the file using async IO
        async with aiofiles.open(filepath, "wb") as buffer:
            # Process in chunks to avoid memory issues with large files
            CHUNK_SIZE = 1024 * 1024  # 1MB chunks
            while content := await video_file.read(CHUNK_SIZE):
                if not content:
                    break
                await buffer.write(content)
        
        logger.info(f"Video saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving video file: {str(e)}")
        raise VideoProcessingError(f"Failed to save video: {str(e)}")

async def create_video_record(
    patient_id: str,
    exercise_id: str,
    file_path: str,
    file_name: str,
    file_size: int,
    content_type: str
) -> Video:
    """Create a new video record in the database"""
    try:
        collection = MongoDB.get_collection(COLLECTION_NAME)
        
        # Create video record
        video_data = VideoCreate(
            patient_id=patient_id,
            exercise_id=exercise_id,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            content_type=content_type
        )
        
        video_in_db = VideoInDB(**video_data.dict())
        
        # Insert into database
        result = await collection.insert_one(video_in_db.dict(by_alias=True))
  
        # Get the created video
        created_video = await collection.find_one({"_id": result.inserted_id})
        if not created_video:
            raise DatabaseOperationError("Failed to retrieve created video record")
        
        # Now update the corresponding exercise
        exercise_collection = MongoDB.get_collection("exercises")  # <- assume collection name
        update_result = await exercise_collection.update_one(
            {"_id": exercise_id},
            {"$set": {"video_id": result.inserted_id}}
        )
        
        if update_result.modified_count == 0:
            raise Data
        
        logger.info(f"Video record created: {result.inserted_id}")
        return Video(**created_video)
    except Exception as e:
        logger.error(f"Error creating video record: {str(e)}")
        if os.path.exists(file_path):
            try:
                # Clean up file if database operation fails
                os.remove(file_path)
                logger.info(f"Removed video file after failed record creation: {file_path}")
            except Exception as file_e:
                logger.error(f"Failed to remove video file: {str(file_e)}")
        raise DatabaseOperationError(f"Failed to create video record: {str(e)}")

async def get_video(video_id: str) -> Video:
    """Get a video by ID"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    try:
        if not ObjectId.is_valid(video_id):
            raise ResourceNotFoundError(f"Invalid video ID format: {video_id}")
            
        video = await collection.find_one({"_id": ObjectId(video_id)})
        
        if not video:
            logger.warning(f"Video not found: {video_id}")
            raise ResourceNotFoundError(f"Video not found: {video_id}")
        
        logger.debug(f"Retrieved video: {video_id}")
        return Video(**video)
    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving video {video_id}: {str(e)}")
        raise DatabaseOperationError(f"Failed to retrieve video: {str(e)}")

async def update_video_status(video_id: str, new_status: str) -> Video:
    """Update the status of a video"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    try:
        if not ObjectId.is_valid(video_id):
            raise ResourceNotFoundError(f"Invalid video ID format: {video_id}")
            
        # Update the video
        result = await collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            # Check if record exists but wasn't modified
            video = await collection.find_one({"_id": ObjectId(video_id)})
            if not video:
                logger.warning(f"Video not found for status update: {video_id}")
                raise ResourceNotFoundError(f"Video not found: {video_id}")
            # If we got here, the video exists but wasn't modified (e.g., same status)
        
        # Get the updated video
        updated_video = await collection.find_one({"_id": ObjectId(video_id)})
        if not updated_video:
            raise DatabaseOperationError("Failed to retrieve updated video record")
        
        logger.info(f"Updated video status to {new_status}: {video_id}")
        return Video(**updated_video)
    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error updating video status {video_id}: {str(e)}")
        raise DatabaseOperationError(f"Failed to update video status: {str(e)}")

async def delete_video(video_id: str) -> None:
    """Delete a video by ID and remove the file from disk"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    
    try:
        if not ObjectId.is_valid(video_id):
            raise ResourceNotFoundError(f"Invalid video ID format: {video_id}")
            
        # Check if video exists
        video = await collection.find_one({"_id": ObjectId(video_id)})
        if not video:
            logger.warning(f"Video not found for deletion: {video_id}")
            raise ResourceNotFoundError(f"Video not found: {video_id}")
        
        # Get the file path before deleting the record
        file_path = video["file_path"]
        
        # Delete the video record
        result = await collection.delete_one({"_id": ObjectId(video_id)})
        if result.deleted_count == 0:
            raise DatabaseOperationError(f"Failed to delete video record: {video_id}")
        
        logger.info(f"Deleted video record: {video_id}")
        
        # Delete the file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted video file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to remove video file {file_path}: {str(e)}")
                # We don't raise here since the database record is already deleted
        else:
            logger.warning(f"Video file not found for deletion: {file_path}")
    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting video {video_id}: {str(e)}")
        raise DatabaseOperationError(f"Failed to delete video: {str(e)}")

async def get_patient_videos(patient_id: str) -> List[Video]:
    """Get all videos uploaded by a patient"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    videos = []
    
    try:
        if not ObjectId.is_valid(patient_id):
            logger.warning(f"Invalid patient ID format for video query: {patient_id}")
            return []  # Return empty list for invalid IDs
            
        cursor = collection.find({"patient_id": ObjectId(patient_id)}).sort("upload_date", DESCENDING)
        
        async for video in cursor:
            videos.append(Video(**video))
        
        logger.debug(f"Retrieved {len(videos)} videos for patient {patient_id}")
        return videos
    except Exception as e:
        logger.error(f"Error retrieving videos for patient {patient_id}: {str(e)}")
        raise DatabaseOperationError(f"Failed to retrieve patient videos: {str(e)}")

async def get_exercise_videos(exercise_id: str) -> List[Video]:
    """Get all videos for a specific exercise"""
    collection = MongoDB.get_collection(COLLECTION_NAME)
    videos = []
    
    try:
        if not ObjectId.is_valid(exercise_id):
            logger.warning(f"Invalid exercise ID format for video query: {exercise_id}")
            return []  # Return empty list for invalid IDs
            
        cursor = collection.find({"exercise_id": ObjectId(exercise_id)}).sort("upload_date", DESCENDING)
        
        async for video in cursor:
            videos.append(Video(**video))
        
        logger.debug(f"Retrieved {len(videos)} videos for exercise {exercise_id}")
        return videos
    except Exception as e:
        logger.error(f"Error retrieving videos for exercise {exercise_id}: {str(e)}")
        raise DatabaseOperationError(f"Failed to retrieve exercise videos: {str(e)}") 