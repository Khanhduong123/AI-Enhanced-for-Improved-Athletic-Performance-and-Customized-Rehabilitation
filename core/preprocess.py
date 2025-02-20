import json
import numpy as np
import os

# Hàm đọc file JSON và chuyển thành numpy array
def json_to_numpy(json_file, class_name):
    with open(json_file, "r") as f:
        data = json.load(f)

    if not data:
        print(f"⚠️ Warning: Empty JSON file {json_file}")
        return None, None

    num_frames = len(data)
    num_keypoints = 33  # Số lượng keypoints của Mediapipe
    keypoint_dim = 2  # Chỉ lấy tọa độ (x, y), không dùng z

    keypoints_array = np.zeros((num_frames, num_keypoints, keypoint_dim), dtype=np.float32)

    for i, frame in enumerate(data):
        for j, keypoint in enumerate(frame["pose"].values()):
            keypoints_array[i, j, :] = keypoint  # Gán x, y vào ma trận

    return keypoints_array, class_name  # Trả về tên class dạng string

def process_all_json(input_folder):
    all_data = []
    all_labels = []

    class_folders = [folder for folder in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, folder))]

    for class_name in class_folders:
        class_path = os.path.join(input_folder, class_name)
        json_files = [f for f in os.listdir(class_path) if f.endswith(".json")]

        for json_file in json_files:
            json_path = os.path.join(class_path, json_file)
            keypoints, label = json_to_numpy(json_path, class_name)
            
            if keypoints is not None:
                all_data.append(keypoints)
                all_labels.append(label)

    return np.array(all_data, dtype=object), np.array(all_labels)

# # Đường dẫn đến thư mục chứa JSON output
# json_folder = "../data/keypoints"

# # Chuyển đổi toàn bộ dữ liệu JSON thành numpy array
# X, y = process_all_json(json_folder)

# # Kiểm tra kết quả
# print("✅ Data shape:", X.shape)  # (num_samples, frame, 33, 2)
# print("Keypoints of first sample:", X[0].shape)  # In thử keypoints của mẫu đầu tiên  
# print("✅ Labels shape:", y.shape)  # (num_samples, 1)
# print("Example label:", y[1])  # In thử nhãn của mẫu đầu tiên
