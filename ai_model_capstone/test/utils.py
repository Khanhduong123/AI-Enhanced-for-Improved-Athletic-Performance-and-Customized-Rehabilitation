import cv2
import numpy as np
import os
import random

class VideoAugmentation:
    def __init__(self, video_path):
        self.video_path = video_path
        self.frames = self._load_video().copy()

    def _load_video(self):
        """Load video và trích xuất các frame"""
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            raise ValueError(f"Không thể mở video: {self.video_path}")

        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        cap.release()

        if len(frames) == 0:
            raise ValueError(f"Không có frame nào được trích xuất từ video: {self.video_path}")

        return np.array(frames)

    # Xoay video 90 độ theo chiều kim đồng hồ
    def rotate_90(self):
        self.frames = np.array([
            cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE) 
            for frame in self.frames
        ])
        return self

    # Xoay video 180 độ (chống đầu xuống đất)
    def rotate_180(self):
        self.frames = np.array([
            cv2.rotate(frame, cv2.ROTATE_180) 
            for frame in self.frames
        ])
        return self

    def save_video(self, output_path, fps=30):
        # Tạo thư mục đầu ra nếu chưa tồn tại
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        # Sau khi xoay, kích thước khung hình có thể thay đổi (w,h -> h,w)
        h, w = self.frames[0].shape[:2]
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        for frame in self.frames:
            out.write(frame)
        out.release()
        print(f"Augmented video saved to {output_path}")

def process_videos(input_folder="video/raw", output_folder="video/preprocess"):
    # Duyệt qua tất cả các class trong thư mục raw
    for class_name in os.listdir(input_folder):
        class_path = os.path.join(input_folder, class_name)

        # Kiểm tra xem có phải thư mục không
        if not os.path.isdir(class_path):
            continue

        # Duyệt qua từng file video trong class
        for video_file in os.listdir(class_path):
            if video_file.endswith(".mp4"):  # Chỉ xử lý file MP4
                input_video_path = os.path.join(class_path, video_file)
                output_video_path = os.path.join(output_folder, class_name, video_file)

                print(f"Processing: {input_video_path} -> {output_video_path}")

                # Khởi tạo đối tượng augmentation
                augmenter = VideoAugmentation(input_video_path)

                # Xoay video 90 độ
                augmenter.rotate_90()

                # Lưu video đã xử lý
                augmenter.save_video(output_video_path, fps=30)

if __name__ == "__main__":
    input_path = "../ai_model_capstone/test/video/raw"
    output_path = "../ai_model_capstone/test/video/preprocess"
    process_videos(input_path, output_path)
