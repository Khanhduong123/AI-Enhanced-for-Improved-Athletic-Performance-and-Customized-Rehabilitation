import os
import torch
import numpy as np
import cv2
import mediapipe as mp
import sys
import csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.model import SPOTER, YogaGCN  # Import model từ core.model

# Khởi tạo MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def load_model(model_path, model_name, num_classes):
    """Load model từ checkpoint."""
    if model_name == "spoter":
        model = SPOTER(hidden_dim=72, num_classes=num_classes, max_frame=100, num_heads=9, encoder_layers=1, decoder_layers=1)
    elif model_name == "gcn":
        model = YogaGCN(in_channels=3, hidden_dim=128, num_classes=num_classes)  # Sửa lỗi đánh máy
    else:
        raise ValueError(f"No matching model found: {model_name}")

    # Load checkpoint
    checkpoint = torch.load(model_path, map_location=torch.device("cpu"))
    if "model" in checkpoint:
        print("Loading state_dict from checkpoint...")
        model.load_state_dict(checkpoint["model"], strict=False)
    else:
        print("Warning: Checkpoint does not contain 'model', loading entire state_dict.")
        model.load_state_dict(checkpoint, strict=False)

    model.eval()  # Đưa model vào chế độ evaluation
    return model

def extract_skeleton_from_video(video_path, max_frames=100):
    """Trích xuất keypoints từ video."""
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

        # Đảm bảo luôn có 33 keypoints
        if len(keypoints) != 33:
            keypoints = [[0, 0, 0]] * 33

        skeleton_data.append(keypoints)

    cap.release()
    skeleton_data = np.array(skeleton_data)  # Shape: (num_frames, 33, 3)

    if skeleton_data.shape[1] != 33:
        raise ValueError(f"Keypoints không đúng! Current size: {skeleton_data.shape}")

    return skeleton_data

def normalize_skeleton(skeleton):
    """Chuẩn hóa bộ xương bằng cách dịch tâm về gốc tọa độ."""
    if skeleton.size == 0:
        raise ValueError("Error: Empty skeleton, cannot normalize!")

    mean_pose = np.mean(skeleton[:, :, :2], axis=(0, 1))  # Trung bình trên trục x, y
    skeleton[:, :, :2] -= mean_pose  # Dịch về trung tâm
    return skeleton

def predict_action(video_path, model, model_name, classes):
    """Nhận diện động tác từ video và trả về confidence score."""
    skeleton = extract_skeleton_from_video(video_path)
    skeleton = normalize_skeleton(skeleton)
    skeleton_tensor = torch.tensor(skeleton, dtype=torch.float32)

    with torch.no_grad():
        if model_name == 'spoter':
            skeleton_tensor = skeleton_tensor.view(1, -1)  # Flatten (1, 9900)
            outputs = model(skeleton_tensor)
        else:
            num_frames, num_keypoints, keypoint_dim = skeleton.shape
            skeleton_tensor = skeleton_tensor.view(num_frames * num_keypoints, keypoint_dim)
            batch = torch.zeros(num_frames * num_keypoints, dtype=torch.long)
            edge_index = get_edge_index()
            outputs = model(skeleton_tensor, edge_index, batch)

        probs = torch.nn.functional.softmax(outputs, dim=1)  # Chuyển đổi thành xác suất
        preds = probs.argmax(dim=1).item()
        confidence_score = probs.max(dim=1)[0].item()  # Lấy xác suất cao nhất

    return classes[preds], confidence_score

def get_edge_index():
    """Trả về danh sách cạnh trong đồ thị xương."""
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

def main():
    """Chạy test trên dataset và lưu kết quả."""
    data_dir = r"D:\Thesis_SP25\work\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\test\video\preprocess\Oppo"
    output_csv = r"D:\Thesis_SP25\work\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\test\result\result_spoter_raw_90.csv"

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)  # Tạo thư mục nếu chưa có

    model_name = "spoter"
    if model_name == "spoter":
        model_path = r"D:\Thesis_SP25\work\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\checkpoints\spoter\pretrain\best_checkpoint.pt"
    else:
        model_path = r"D:\Thesis_SP25\work\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\checkpoints\gcn\pretrain\best_checkpoint.pt"

    CLASS_LABELS = [
        "Garland_Pose", "Happy_Baby_Pose", "Head_To_Knee_Pose", "Lunge_Pose",
        "Mountain_Pose", "Plank_Pose", "Raised_Arms_Pose", "Seated_Forward_Bend",
        "Staff_Pose", "Standing_Forward_Bend"
    ]

    model = load_model(model_path, model_name, num_classes=len(CLASS_LABELS))
    
    with open(output_csv, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Video Name", "Predicted Class", "Actual Class", "Confidence Score", "Correct"])

        for class_name in os.listdir(data_dir):
            class_path = os.path.join(data_dir, class_name)
            if not os.path.isdir(class_path):
                continue

            for file_name in os.listdir(class_path):
                if not file_name.endswith(".mp4"):
                    continue

                video_path = os.path.join(class_path, file_name)
                try:
                    print(f"Processing {video_path}...")
                    predicted_class, confidence = predict_action(video_path, model, model_name, CLASS_LABELS)
                    is_correct = (predicted_class == class_name)
                    writer.writerow([file_name, predicted_class, class_name, confidence, is_correct])
                except Exception as e:
                    print(f"Lỗi xử lý {video_path}: {e}")

if __name__ == "__main__":
    main()
