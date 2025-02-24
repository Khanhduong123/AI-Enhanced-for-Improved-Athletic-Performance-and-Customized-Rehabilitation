import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
import json

# Hàm đọc file JSON và chuyển thành numpy array
def json_to_numpy(json_file, class_name):
    with open(json_file, "r") as f:
        data = json.load(f)

    if not data:
        print(f"Warning: Empty JSON file {json_file}")
        return None, None

    num_frames = len(data)
    num_keypoints = 33  # Số lượng keypoints của Mediapipe
    keypoint_dim = 3  # x, y, z

    keypoints_array = np.zeros((num_frames, num_keypoints, keypoint_dim), dtype=np.float32)

    for i, frame in enumerate(data):
        for j, keypoint in enumerate(frame["pose"].values()):
            keypoints_array[i, j, :] = keypoint  # Gán x, y, z vào ma trận

    return keypoints_array, class_name  # Trả về tên class dạng string

# Dataset PyTorch
class YogaDataset(Dataset):
    def __init__(self, json_folder, max_frames=100):
        self.data = []
        self.labels = []
        self.max_frames = max_frames
        self.label_map = {}  # Mapping từ tên class thành số

        # Lấy danh sách class từ thư mục
        class_folders = [folder for folder in os.listdir(json_folder) if os.path.isdir(os.path.join(json_folder, folder))]

        # Gán ID cho từng class (string → int)
        self.label_map = {class_name: idx for idx, class_name in enumerate(class_folders)}
        print("Label map:", self.label_map)

        for class_name in class_folders:
            class_path = os.path.join(json_folder, class_name)
            json_files = [f for f in os.listdir(class_path) if f.endswith(".json")]

            for json_file in json_files:
                json_path = os.path.join(class_path, json_file)
                keypoints, label = json_to_numpy(json_path, class_name)  # label là string
                
                if keypoints is not None:
                    # **Padding hoặc Truncation**
                    padded_keypoints = np.zeros((self.max_frames, 33, 3), dtype=np.float32)  # Sửa (33, 2) thành (33, 3)
                    num_frames = min(len(keypoints), self.max_frames)
                    padded_keypoints[:num_frames, :, :] = keypoints[:num_frames, :, :]  # Cắt hoặc giữ nguyên
                    
                    self.data.append(padded_keypoints)
                    self.labels.append(self.label_map[str(label)])  # Đảm bảo label là string trước khi tra cứu

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        keypoints = self.data[idx]
        label = self.labels[idx]
        return torch.tensor(keypoints, dtype=torch.float32), torch.tensor(label, dtype=torch.long)

if __name__ == "__main__":
    # Khởi tạo dataset và dataloader với max_frames cố định
    json_folder = "../data/keypoints/public_data"
    dataset = YogaDataset(json_folder, max_frames=100)  # Định nghĩa số frame cố định

    batch_size = 4
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Kiểm tra 1 batch dữ liệu
    for batch in dataloader:
        X_batch, y_batch = batch
        print("X_batch shape:", X_batch.shape)  # (batch_size, max_frames, 33, 3)
        print("y_batch shape:", y_batch.shape)  # (batch_size,)
        print("y_batch values:", y_batch)  # Nhãn của từng sample
        break  # Dừng sau batch đầu tiên
