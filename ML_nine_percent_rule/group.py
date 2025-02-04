import os
import csv
import cv2
import mediapipe as mp

# Khởi tạo các label cho các keypoints
pose_landmark_labels = {
    0: "NOSE",
    1: "LEFT_EYE_INNER",
    2: "LEFT_EYE",
    3: "LEFT_EYE_OUTER",
    4: "RIGHT_EYE_INNER",
    5: "RIGHT_EYE",
    6: "RIGHT_EYE_OUTER",
    7: "LEFT_EAR",
    8: "RIGHT_EAR",
    9: "MOUTH_LEFT",
    10: "MOUTH_RIGHT",
    11: "LEFT_SHOULDER",   
    12: "RIGHT_SHOULDER",  
    13: "LEFT_ELBOW",     
    14: "RIGHT_ELBOW",     
    15: "LEFT_WRIST",      
    16: "RIGHT_WRIST",     
    17: "LEFT_PINKY",      
    18: "RIGHT_PINKY",     
    19: "LEFT_INDEX",      
    20: "RIGHT_INDEX",     
    21: "LEFT_THUMB",      
    22: "RIGHT_THUMB",    
    23: "LEFT_HIP",        
    24: "RIGHT_HIP",       
    25: "LEFT_KNEE",       
    26: "RIGHT_KNEE",      
    27: "LEFT_ANKLE",      
    28: "RIGHT_ANKLE",     
    29: "LEFT_HEEL",       
    30: "RIGHT_HEEL",      
    31: "LEFT_FOOT_INDEX",
    32: "RIGHT_FOOT_INDEX"
}

# Các nhóm keypoint
KEYPOINT_GROUPS = {
    "FACE_NECK": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "RIGHT_ARM": [12, 14, 16, 18, 20, 22],
    "LEFT_ARM": [11, 13, 15, 17, 19, 21],
    "RIGHT_LEG": [24, 26, 28, 30, 32],
    "LEFT_LEG": [23, 25, 27, 29, 31],
    "BODY": [11, 12, 23, 24]
}

# Hàm trích xuất tọa độ x, y, z từ nhóm keypoint
def extract_keypoint_coordinates(results, group_ids, width, height):
    coordinates = []
    for landmark_id in group_ids:
        landmark = results.pose_landmarks.landmark[landmark_id]
        x = landmark.x * width
        y = landmark.y * height
        z = landmark.z  # Độ sâu
        coordinates.extend([x, y, z])  # Lưu x, y, z vào danh sách
    return coordinates

# Hàm xử lý ảnh và lưu dữ liệu vào file CSV
def process_images_and_save_to_csv(folder_path, output_folder):
    # Khởi tạo MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)

    # Đọc tất cả ảnh trong thư mục
    image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpg")]

    # Khởi tạo danh sách cho các bộ phận cơ thể
    coordinates_by_group = {group: [] for group in KEYPOINT_GROUPS}

    # Xử lý tất cả các ảnh trong thư mục
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        # Lấy kích thước ảnh
        height, width, _ = image.shape

        # Nếu phát hiện được các keypoints
        if results.pose_landmarks:
            for group_name, ids in KEYPOINT_GROUPS.items():
                coordinates = extract_keypoint_coordinates(results, ids, width, height)
                coordinates_by_group[group_name].append(coordinates)

    # Tạo thư mục để lưu các file CSV nếu chưa tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Lưu dữ liệu vào các file CSV riêng biệt cho mỗi bộ phận cơ thể
    for group_name, coordinates_list in coordinates_by_group.items():
        file_path = os.path.join(output_folder, f"{group_name}_coordinates.csv")
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            
            # Tạo các tiêu đề cột
            header = []
            for i in range(1, len(KEYPOINT_GROUPS[group_name]) + 1):
                header.extend([f"{group_name}_{i}_x", f"{group_name}_{i}_y", f"{group_name}_{i}_z"])
            writer.writerow(header)
            
            # Viết các tọa độ vào file
            for coordinates in coordinates_list:
                writer.writerow(coordinates)

        print(f"Đã lưu dữ liệu của {group_name} vào file {file_path}")

# Định nghĩa đường dẫn thư mục input và output
input_folder = "output_data2/processed_keyframes"  # Đường dẫn thư mục chứa ảnh
output_folder = "pose_data_csv2"  # Đường dẫn thư mục để lưu CSV

# Xử lý ảnh và lưu dữ liệu
process_images_and_save_to_csv(input_folder, output_folder)