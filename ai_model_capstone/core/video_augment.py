import cv2
import numpy as np
import random
import os

class VideoAugmentation:
    def __init__(self, video_path):
        self.video_path = video_path
        self.frames = self._load_video()

    def _load_video(self):
        """ Load video và trích xuất các frame """
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

    def rotation(self, angle=15):
        h, w = self.frames[0].shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        self.frames = np.array([cv2.warpAffine(frame, M, (w, h)) for frame in self.frames])
        return self

    def horizontal_flip(self):
        self.frames = np.array([cv2.flip(frame, 1) for frame in self.frames])
        return self

    def change_speed(self, speed_factor=1.2):
        num_frames = int(len(self.frames) * speed_factor)
        indices = np.linspace(0, len(self.frames) - 1, num_frames, dtype=int)
        self.frames = self.frames[indices]
        return self

    def frame_dropout(self, drop_ratio=0.2):
        num_frames = len(self.frames)
        num_drop = int(num_frames * drop_ratio)
        drop_indices = random.sample(range(num_frames), num_drop)
        self.frames = np.delete(self.frames, drop_indices, axis=0)
        return self

    def save_video(self, output_path, fps = 30): # tự nó lấy ra fps luôn chứ kh có ép cứng
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        h, w = self.frames[0].shape[:2]
        out = cv2.VideoWriter(output_path, fourcc,fps ,(w, h))

        for frame in self.frames:
            out.write(frame)
        out.release()
        print(f"Augmented video saved to {output_path}")

def process_videos(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for class_folder in os.listdir(input_folder):
        class_path = os.path.join(input_folder, class_folder)
        output_class_path = os.path.join(output_folder, class_folder)

        if not os.path.isdir(class_path):
            continue  # Bỏ qua nếu không phải thư mục

        if not os.path.exists(output_class_path):
            os.makedirs(output_class_path)

        for video_file in os.listdir(class_path):
            if not video_file.endswith(".mp4"):
                continue  
            
            video_path = os.path.join(class_path, video_file)
            base_name = os.path.splitext(video_file)[0]  # Lấy tên file không có đuôi .mp4

            # Tạo instance của VideoAugmentation
            augmenter = VideoAugmentation(video_path)

            # Lưu các video augment vào thư mục tương ứng
            augmenter.rotation(angle=10).save_video(os.path.join(output_class_path, f"{base_name}_rotation.mp4"))
            augmenter.horizontal_flip().save_video(os.path.join(output_class_path, f"{base_name}_flip.mp4"))
            augmenter.change_speed(speed_factor=1.2).save_video(os.path.join(output_class_path, f"{base_name}_speedup.mp4"))
            augmenter.frame_dropout(drop_ratio=0.2).save_video(os.path.join(output_class_path, f"{base_name}_dropout.mp4"))

if __name__ == "__main__":
    input_path = os.path.join(os.getcwd(), "data", "raw_video", "public_data")

    output_path = os.path.join(os.getcwd(), "data", "processed_video", "public_data")

    process_videos(input_path, output_path)