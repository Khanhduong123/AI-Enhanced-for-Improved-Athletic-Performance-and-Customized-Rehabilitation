import cv2
import numpy as np
import os

import cv2
import numpy as np
import os

class VideoAugmentation:
    def __init__(self, video_path):
        self.video_path = video_path
        self.original_frames = self._load_video()  # Lưu frames gốc
        self.frames = self.original_frames.copy()  # Bản sao để augment

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

    def reset_frames(self):
        """Reset frames về trạng thái gốc trước khi augment"""
        self.frames = self.original_frames.copy()

    # Xoay video 90 độ theo chiều kim đồng hồ
    def rotate_90(self):
        self.reset_frames()
        self.frames = np.array([
            cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            for frame in self.frames
        ])
        return self

    # Xoay video 180 độ (chống đầu xuống đất)
    def rotate_180(self):
        self.reset_frames()
        self.frames = np.array([
            cv2.rotate(frame, cv2.ROTATE_180)
            for frame in self.frames
        ])
        return self

    # Làm mờ video bằng Gaussian Blur
    def apply_blur(self, kernel_size=(5, 5)):
        """
        Làm mờ mỗi frame trong video bằng bộ lọc Gaussian Blur.
        kernel_size: Kích thước kernel (nên là số lẻ, ví dụ: (5,5) hoặc (7,7))
        """
        self.reset_frames()
        self.frames = np.array([
            cv2.GaussianBlur(frame, kernel_size, 0)
            for frame in self.frames
        ])
        return self

    def save_video(self, output_path, fps=30):
        """Lưu video sau khi xử lý"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Sau khi xử lý, kích thước khung hình có thể thay đổi (w,h -> h,w)
        h, w = self.frames[0].shape[:2]
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        for frame in self.frames:
            out.write(frame)
        out.release()
        print(f"Augmented video saved to {output_path}")
 

def process_videos(input_folder="video/raw", output_folder="video/preprocess"):
    """Duyệt qua tất cả các class trong thư mục raw và lưu kết quả vào preprocess"""
    for class_name in os.listdir(input_folder):
        class_path = os.path.join(input_folder, class_name)

        # Kiểm tra xem có phải thư mục không
        if not os.path.isdir(class_path):
            continue

        output_class_path = os.path.join(output_folder, class_name)
        os.makedirs(output_class_path, exist_ok=True)  # Tạo thư mục nếu chưa có

        # Duyệt qua từng file video trong class
        for video_file in os.listdir(class_path):
            if video_file.endswith(".mp4"):  # Chỉ xử lý file MP4
                input_video_path = os.path.join(class_path, video_file)
                base_name, _ = os.path.splitext(video_file)  # Lấy tên file không có đuôi .mp4

                # Đường dẫn lưu video đã xử lý
                # output_90_path = os.path.join(output_class_path, f"{base_name}_90.mp4")
                # output_180_path = os.path.join(output_class_path, f"{base_name}_180.mp4")
                output_blur_path = os.path.join(output_class_path, f"{base_name}_blur.mp4")

                print(f"Processing: {input_video_path} ->  {output_blur_path}")

                # Khởi tạo đối tượng augmentation
                augmenter = VideoAugmentation(input_video_path)

                # Xoay video 90 độ và lưu
                # augmenter.rotate_90()
                # augmenter.save_video(output_90_path, fps=30)

                # # Xoay video 180 độ và lưu
                # augmenter.rotate_180()
                # augmenter.save_video(output_180_path, fps=30)

                # Làm mờ video và lưu
                augmenter.apply_blur(kernel_size=(9, 9))  # Kernel (7,7) giúp làm mờ mạnh hơn
                augmenter.save_video(output_blur_path, fps=30)


if __name__ == "__main__":
    input_path = "../ai_model_capstone/test/video/raw"
    output_path = "../ai_model_capstone/test/video/preprocess"
    process_videos(input_path, output_path)
