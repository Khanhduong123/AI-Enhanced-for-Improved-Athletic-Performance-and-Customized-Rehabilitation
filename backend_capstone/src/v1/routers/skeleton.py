import os
import uuid
import logging
import cv2
import mediapipe as mp
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse

# Set up logging
logger = logging.getLogger(__name__)

# Create the APIRouter
router = APIRouter(prefix="/skeleton", tags=["Skeleton Extraction"])

@router.post("/extract", response_class=FileResponse)
async def extract_skeleton(video_file: UploadFile = File(...)):
    """
    Receive a video file, extract skeleton, and return the processed video.
    
    Parameters:
    - video_file: The uploaded video file (must be in MP4 format, max 50MB)
    
    Returns:
    - Processed video file with skeleton overlay
    
    Raises:
    - HTTPException: If file validation fails or processing encounters an error
    """
    # Validate file type
    if not video_file.content_type or "video" not in video_file.content_type:
        logger.warning(f"Invalid file type: {video_file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a video"
        )
    
    # Create unique filenames for input and output
    input_filename = f"{uuid.uuid4()}_input.mp4"
    output_filename = f"{uuid.uuid4()}_output.mp4"
    
    input_filepath = os.path.join("temp_videos", input_filename)
    output_filepath = os.path.join("temp_videos", output_filename)
    
    os.makedirs("temp_videos", exist_ok=True)

    try:
        # Save the uploaded file
        file_content = await video_file.read()
        
        # Check file size (limit to 50MB)
        if len(file_content) > 50 * 1024 * 1024:  
            logger.warning(f"File too large: {len(file_content) / (1024 * 1024):.2f}MB")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds the 50MB limit"
            )
        
        with open(input_filepath, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Processing video for skeleton extraction: {input_filepath}")

        # Extract skeleton
        extract_skeleton_from_video(input_filepath, output_filepath)
        
        # Convert to a web-compatible format for better streaming
        web_compatible_path = convert_to_web_compatible(output_filepath)
        
        # Return the processed video file
        return FileResponse(
            path=web_compatible_path if os.path.exists(web_compatible_path) else output_filepath, 
            media_type="video/mp4", 
            filename="skeleton_video.mp4",
            background=BackgroundTask(cleanup_files, input_filepath, output_filepath, web_compatible_path)
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        cleanup_files(input_filepath, output_filepath)
        raise
    except Exception as e:
        # Log the error with traceback
        logger.exception(f"Skeleton extraction error: {str(e)}")
        cleanup_files(input_filepath, output_filepath)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing video: {str(e)}"
        )

def extract_skeleton_from_video(input_video_path, output_video_path):
    """
    Extract skeleton from video and save the result.
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        logger.error(f"Could not open video: {input_video_path}")
        raise ValueError("Could not open video file")
    
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Use H.264 codec for better web compatibility
    fourcc = cv2.VideoWriter_fourcc(*'H264') if cv2.VideoWriter_fourcc(*'H264') != -1 else cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        out.write(frame)
        frame_count += 1
        
        if frame_count % 30 == 0:
            logger.debug(f"Processed {frame_count} frames")
    
    cap.release()
    out.release()
    logger.info(f"Skeleton-extracted video saved at: {output_video_path}")

def convert_to_web_compatible(video_path):
    """
    Convert video to a web-compatible format using FFmpeg if available
    """
    try:
        import subprocess
        output_path = f"{os.path.splitext(video_path)[0]}_web.mp4"
        
        # Use FFmpeg to convert to a web-compatible format
        cmd = [
            'ffmpeg', '-i', video_path, 
            '-vcodec', 'libx264', '-acodec', 'aac',
            '-movflags', 'faststart',
            '-pix_fmt', 'yuv420p',
            '-y', output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"Converted video to web-compatible format: {output_path}")
        return output_path
    except Exception as e:
        logger.warning(f"Failed to convert video to web-compatible format: {str(e)}")
        return video_path  # Return original path if conversion fails

from starlette.background import BackgroundTask

def cleanup_files(*filepaths):
    """Remove temporary files after response is sent"""
    for filepath in filepaths:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.debug(f"Removed temporary file: {filepath}")
            except Exception as e:
                logger.error(f"Failed to remove temporary file {filepath}: {str(e)}")