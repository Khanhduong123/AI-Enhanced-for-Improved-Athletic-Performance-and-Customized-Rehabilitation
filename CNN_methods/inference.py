import cv2
import mediapipe as mp
from collections import deque
import logging

import torch
import cv2
import mediapipe as mp
import numpy as np
from torchvision import transforms
from model import SimpleCNN  # Import model của bạn
from utils import build_transforms

mp_pose = mp.solutions.pose
# Hàm để xử lý khung hình đầu vào và trích xuất landmarks
def preprocess_frame(frame, pose, device, transform):
    """
    Xử lý frame: Trích xuất landmarks từ Mediapipe và chuyển thành tensor.
    """
    # Chuyển khung hình sang định dạng RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    # Vẽ landmarks trên ảnh
    annotated_frame = frame.copy()
    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            annotated_frame, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS
        )

    # Nếu phát hiện landmarks, chuyển thành tensor
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        # Tạo hình ảnh trống từ các landmarks
        blank_image = generate_pose_image(landmarks)
        input_tensor = transform(blank_image).unsqueeze(0).to(device)  # Thêm batch dimension
        return input_tensor, annotated_frame
    else:
        return None, annotated_frame


# Hàm để xử lý ảnh và tạo tensor đầu vào
def preprocess_image(image_path, transform, device):
    """
    Xử lý ảnh từ tệp và chuyển thành tensor.
    """
    # Đọc ảnh từ tệp
    image = cv2.imread(image_path)

    # Kiểm tra nếu ảnh không được tải
    if image is None:
        print(f"Không thể đọc ảnh từ: {image_path}")
        return None

    # Chuyển ảnh sang RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Dùng các transform đã định nghĩa
    input_tensor = transform(image_rgb).unsqueeze(0).to(device)  # Thêm batch dimension
    return input_tensor, image

# Hàm để tạo ảnh trống từ pose landmarks
def generate_pose_image(landmarks):
    """
    Tạo một hình ảnh trống (blank image) từ pose landmarks.
    """
    blank_image = 255 * np.ones((224, 224, 3), dtype=np.uint8)
    for landmark in landmarks:
        x = int(landmark.x * 224)
        y = int(landmark.y * 224)
        cv2.circle(blank_image, (x, y), 5, (0, 0, 255), -1)
    return blank_image

# Hàm main để chạy toàn bộ quá trình inference
def main():
    # Thiết lập device và load model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SimpleCNN(num_classes=2).to(device)

    checkpoint_path = "./checkpoint/checkpoint.pt"  # Đường dẫn tới checkpoint của bạn
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model'])
    model.eval()  # Chuyển mô hình sang chế độ inference

    # Thiết lập OpenCV để đọc video/webcam
    cap = cv2.VideoCapture(0)  # Thay '0' bằng đường dẫn video nếu cần

    # Thiết lập Mediapipe để phát hiện pose landmarks
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # Các transformations cho mô hình
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),  # Resize ảnh
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Chuẩn hóa
    ])
    # Danh sách các động tác (có thể mở rộng thêm)
    action_labels = ["Barbell Curl", "Hammer Curl"]

    # Biến lưu trạng thái hiện tại (ban đầu là "Unknown")
    current_label = "Unknown"

    frame_count = 0  # Biến đếm số frame
    warmup_frames = 60

    # Vòng lặp chính để xử lý từng khung hình
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        
        if frame_count > warmup_frames and frame_count % 10 == 0:  # Dự đoán mỗi 10 frame sau khi warmup
            input_tensor, annotated_frame = preprocess_frame(frame, pose, device, transform)

            if input_tensor is not None:
                with torch.no_grad():
                    output = model(input_tensor)
                    _, predicted = torch.max(output, 1)
                    
                    # Kiểm tra nếu chỉ số dự đoán hợp lệ
                    if 0 <= predicted.item() < len(action_labels):
                        current_label = action_labels[predicted.item()]
                    else:
                        current_label = "Unknown"

            # Hiển thị nhãn dự đoán trên khung hình
            cv2.putText(annotated_frame, current_label, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Hiển thị khung hình
            cv2.imshow("Pose Detection and Classification", annotated_frame)

        # Thoát khi nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
