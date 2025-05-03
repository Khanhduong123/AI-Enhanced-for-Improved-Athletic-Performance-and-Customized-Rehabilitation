import os
import torch
import numpy as np
import cv2
import mediapipe as mp
from typing import List

# If you place SPOTER and YogaGCN in the same directory, import them accordingly:
# from .model_definitions import SPOTER, YogaGCN
# Or if you keep them in a "core.model" or similar path, adjust the import:
# from core.model import SPOTER, YogaGCN

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


def load_model(model_path: str, model, strict_load: bool = False):
    """
    Load checkpoint into a given model instance.
    """
    checkpoint = torch.load(model_path, map_location=torch.device("cpu"), weights_only=False)
    if "model" in checkpoint:
        print("Loading state_dict from checkpoint...")
        model.load_state_dict(checkpoint["model"], strict=strict_load)
    else:
        print("Warning: Checkpoint does not contain 'model', loading entire state_dict.")
        model.load_state_dict(checkpoint, strict=strict_load)
    model.eval()
    return model


def extract_skeleton_from_video(video_path: str, max_frames: int = 100):
    """
    Extract 33 pose keypoints from the input video using MediaPipe Pose.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        raise ValueError(f"Video {video_path} has no frames!")

    indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
    skeleton_data = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            print(f"Cannot read frame {idx}")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        keypoints = []
        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                keypoints.append([lm.x, lm.y, lm.z])

        if len(keypoints) != 33:
            keypoints = [[0, 0, 0]] * 33

        skeleton_data.append(keypoints)

    cap.release()
    skeleton_data = np.array(skeleton_data)  # Shape: (num_frames, 33, 3)

    if skeleton_data.shape[1] != 33:
        raise ValueError(f"Keypoints are incorrect! Current shape: {skeleton_data.shape}")

    return skeleton_data


def normalize_skeleton(skeleton: np.ndarray):
    """
    Normalize skeleton by shifting x,y coords to the center.
    """
    if skeleton.size == 0:
        raise ValueError("Empty skeleton, cannot normalize!")
    mean_pose = np.mean(skeleton[:, :, :2], axis=(0, 1))
    skeleton[:, :, :2] -= mean_pose
    return skeleton


def get_edge_index():
    """
    Build edges for the GCN model. 
    Returns a torch.tensor with shape [2, num_edges].
    """
    import torch
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 7),  # Left arm
        (0, 4), (4, 5), (5, 6), (6, 8),  # Right arm
        (9, 10), (11, 12),  # Hips
        (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),  # Left leg
        (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),  # Right leg
        (11, 23), (12, 24), (23, 24),  # Connect hips
        (23, 25), (25, 27), (27, 29), (29, 31),  # Left leg
        (24, 26), (26, 28), (28, 30), (30, 32)   # Right leg
    ]
    return torch.tensor(edges, dtype=torch.long).t().contiguous()


def predict_action(
    video_path: str, 
    model: torch.nn.Module, 
    model_name: str, 
    classes: List[str]
) -> dict:
    """
    Given a video, extract skeleton keypoints, run through the specified model, 
    and return the predicted class label.
    """
    try:
        skeleton = extract_skeleton_from_video(video_path)
        if skeleton.size == 0:
            raise ValueError(f"Empty skeleton from video {video_path}!")

        skeleton = normalize_skeleton(skeleton)
        skeleton_tensor = torch.tensor(skeleton, dtype=torch.float32)

        with torch.no_grad():
            if model_name == 'spoter':
                # Flatten shape (num_frames, 33, 3) → (1, 9900)
                skeleton_tensor = skeleton_tensor.unsqueeze(0)  # (1, num_frames, 33, 3)
                skeleton_tensor = skeleton_tensor.view(1, -1)   # (1, 9900)
                outputs = model(skeleton_tensor).squeeze(1)
                preds = outputs.argmax(dim=1)
            else:
                # For GCN model
                num_frames, num_keypoints, keypoint_dim = skeleton.shape
                skeleton_tensor = skeleton_tensor.view(num_frames * num_keypoints, keypoint_dim)
                batch = torch.zeros(num_frames * num_keypoints, dtype=torch.long)
                edge_index = get_edge_index()
                outputs = model(skeleton_tensor, edge_index, batch)
                preds = outputs.argmax(dim=1)

        # Lấy giá trị confidence
        raw_confidence = float(outputs.max().item())
        
        # Chuẩn hóa giá trị confidence về 0-1
        # Phương pháp 1: Giới hạn trực tiếp
        normalized_confidence = min(raw_confidence, 1.0)
        
        # Phương pháp 2: Áp dụng softmax (nếu mô hình chưa áp dụng)
        # outputs_softmax = torch.nn.functional.softmax(outputs, dim=1)
        # normalized_confidence = float(outputs_softmax.max().item())
        
        result = {
            "class": classes[preds],
            "confidence": normalized_confidence, # Sử dụng giá trị đã chuẩn hóa
            "features": []
        }
        return result
    except Exception as e:
        print(f"Error in predict_action: {str(e)}")
        return {
            "class": "Unknown",
            "confidence": 0.0,
            "features": [],
            "error": str(e)
        }
