import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
import json

# Hàm đọc file JSON và chuyển thành numpy array
def json_to_numpy(json_file, class_name, target_fps=30, original_fps=60):
    with open(json_file, "r") as f:
        data = json.load(f)

    if not data:
        print(f"⚠️ Warning: Empty JSON file {json_file}")
        return None, None

    num_keypoints = 33  # Mediapipe có 33 keypoints
    keypoint_dim = 2  # Chỉ lấy tọa độ (x, y)

    # Lấy mẫu lại dữ liệu để từ 60 FPS → 30 FPS
    step = original_fps // target_fps  # step = 60 // 30 = 2
    sampled_data = data[::step]  # Chọn mỗi frame thứ 2

    num_frames = len(sampled_data)
    keypoints_array = np.zeros((num_frames, num_keypoints, keypoint_dim), dtype=np.float32)

    for i, frame in enumerate(sampled_data):
        pose_dict = frame["pose"]
        keypoints = np.zeros((num_keypoints, keypoint_dim), dtype=np.float32)

        for j, keypoint_name in enumerate(pose_dict.keys()):
            keypoints[j, :] = pose_dict[keypoint_name]  # Lấy tọa độ x, y

        keypoints_array[i] = keypoints  # Gán vào frame i

    return keypoints_array, class_name  # Trả về numpy array & tên class dạng string

# Dataset PyTorch
class KeypointDataset(Dataset):
    def __init__(self, json_folder, target_fps=30, original_fps=60):
        self.data = []
        self.labels = []
        self.label_map = {}  # Mapping class_name -> ID

        # Lấy danh sách các thư mục class
        class_folders = [folder for folder in os.listdir(json_folder) if os.path.isdir(os.path.join(json_folder, folder))]
        
        # Gán ID cho từng class
        self.label_map = {class_name: idx for idx, class_name in enumerate(class_folders)}

        for class_name in class_folders:
            class_path = os.path.join(json_folder, class_name)
            json_files = [f for f in os.listdir(class_path) if f.endswith(".json")]

            for json_file in json_files:
                json_path = os.path.join(class_path, json_file)
                keypoints, label = json_to_numpy(json_path, class_name, target_fps, original_fps)

                if keypoints is not None:
                    self.data.append(keypoints)
                    self.labels.append(self.label_map[str(label)])  

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        keypoints = self.data[idx]
        label = self.labels[idx]
        return torch.tensor(keypoints, dtype=torch.float32), torch.tensor(label, dtype=torch.long)

# 📌 Hàm padding batch video ngắn hơn
def collate_fn_padding(batch):
    """Padding video ngắn hơn trong batch để đảm bảo tất cả có cùng số frame"""
    batch.sort(key=lambda x: x[0].shape[0], reverse=True)  # Sắp xếp giảm dần theo số frame
    max_frames = batch[0][0].shape[0]  # Số frame của video dài nhất trong batch

    batch_padded = []
    labels = []

    for keypoints, label in batch:
        num_frames = keypoints.shape[0]
        pad_size = max_frames - num_frames

        # Padding video ngắn hơn bằng 0
        padded_keypoints = torch.cat([keypoints, torch.zeros((pad_size, 33, 2))], dim=0)
        batch_padded.append(padded_keypoints)
        labels.append(label)

    return torch.stack(batch_padded), torch.tensor(labels)

if __name__ == "__main__":
    # Khởi tạo dataset và dataloader với padding
    json_folder = "../data/keypoints"
    dataset = KeypointDataset(json_folder, target_fps=30, original_fps=60)

    batch_size = 4
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn_padding)

    # Kiểm tra 1 batch dữ liệu
    for batch in dataloader:
        X_batch, y_batch = batch
        print("✅ X_batch shape:", X_batch.shape)  # (batch_size, max_frames_in_batch, 33, 2)
        print("✅ y_batch shape:", y_batch.shape)  # (batch_size,)
        print("✅ y_batch values:", y_batch)  # Nhãn của từng sample
        break  # Dừng sau batch đầu tiên
