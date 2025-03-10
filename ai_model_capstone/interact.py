import os
import torch
import numpy as np
import cv2
import mediapipe as mp
from core.model import SPOTER, YogaGCN


mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


def load_model(model_path, model_name, num_classes=4):
    """Load model from checkpoint"""
    if model_name == "spoter":
        model = SPOTER(hidden_dim=72, num_classes=num_classes, num_heads=9, encoder_layers=6, decoder_layers=6)
    elif model_name == "gcn":
        model = YogaGCN(in_channels=3, hidden_dim=128, num_classes=num_classes)
    else:
        raise ValueError(f"No matching model found: {model_name}")

    #Load checkpoint
    checkpoint = torch.load(model_path, map_location=torch.device("cpu"))
    if "model" in checkpoint:
        print("Loading state_dict from checkpoint...")
        model.load_state_dict(checkpoint["model"], strict=False)
    else:
        print("Warning: Checkpoint does not contain 'model', loading entire state_dict.")
        model.load_state_dict(checkpoint, strict=False)

    model.eval()  # Đưa model vào chế độ evaluation
    return model


def extract_skeleton_from_video(video_path, max_frames=100 ):#numframes = 100
    """Extract keypoints from video and make sure the output has exactly 33 keypoints"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise FileNotFoundError(f"Không thể mở video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        raise ValueError(f"Video {video_path} không có frame nào!")

    indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
    skeleton_data = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            print(f"Không thể đọc frame {idx}")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        keypoints = []
        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                keypoints.append([lm.x, lm.y, lm.z])

        if len(keypoints) != 33:  # Đảm bảo luôn có 33 keypoints
            keypoints = [[0, 0, 0]] * 33

        skeleton_data.append(keypoints)

    cap.release()
    skeleton_data = np.array(skeleton_data)  # Shape: (num_frames, 33, 3)

    if skeleton_data.shape[1] != 33:
        raise ValueError(f"Keypoints are incorrect! Current size: {skeleton_data.shape}")

    return skeleton_data


def normalize_skeleton(skeleton):
    """Normalize skeleton by shifting coordinates to the center"""
    if skeleton.size == 0:
        raise ValueError("Error: Empty skeleton, cannot normalize!")

    mean_pose = np.mean(skeleton[:, :, :2], axis=(0, 1))  # Trung bình trên trục x, y
    skeleton[:, :, :2] -= mean_pose  # Dịch về trung tâm
    return skeleton


def predict_action(video_path, model, model_name, classes):
    """Take input video, extract skeleton, and predict gesture."""
    skeleton = extract_skeleton_from_video(video_path)
    print(skeleton.shape)

    if skeleton.size == 0:
        raise ValueError(f"Skeleton rỗng từ video {video_path}!")

    print(f"Dữ liệu skeleton: {skeleton.shape}")  # Debug

    skeleton = normalize_skeleton(skeleton)
    skeleton_tensor = torch.tensor(skeleton, dtype=torch.float32)
    print(skeleton_tensor.shape)

    with torch.no_grad():
        if model_name == 'spoter':
            skeleton_tensor = skeleton_tensor.unsqueeze(0)  # Flatten thành (1, 9900)
            skeleton_tensor = skeleton_tensor.view(1, -1)  # Flatten thành (1, 9900)
            outputs = model(skeleton_tensor).squeeze(1)
            preds = outputs.argmax(dim=1)
        else:
            num_frames, num_keypoints, keypoint_dim = skeleton.shape
            skeleton_tensor = skeleton_tensor.view(num_frames * num_keypoints, keypoint_dim)
            batch = torch.zeros(num_frames * num_keypoints, dtype=torch.long)
            edge_index = get_edge_index()
            outputs = model(skeleton_tensor, edge_index, batch)
            preds = outputs.argmax(dim=1)

    return classes[preds]


def get_edge_index():
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 7),  
        (0, 4), (4, 5), (5, 6), (6, 8),  
        (9, 10), (11, 12), 
        (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),  
        (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),  
        (11, 23), (12, 24), (23, 24),  
        (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),  
        (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)   
    ]
    return torch.tensor(edges, dtype=torch.long).t().contiguous()


if __name__ == "__main__":
    model_name = 'gcn'
    num_classes = 4
    checkpoint_path = os.path.abspath("checkpoints/gcn/pretrain/best_checkpoint.pt")
    model = load_model(checkpoint_path, model_name, num_classes)

    classes = ["Garland_Pose", "Happy_Baby_Pose", "Head_To_Knee_Pose", "Lunge_Pose"]
    video_path = os.path.abspath("data/raw_video/public_data/Garland_Pose/sample1.mp4")

    predict_action = predict_action(video_path, model, model_name, classes)
    print(f"Predicted results: {predict_action}")