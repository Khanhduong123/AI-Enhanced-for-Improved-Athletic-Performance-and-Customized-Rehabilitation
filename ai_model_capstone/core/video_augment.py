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

    def save_video(self, output_path, fps=30):
        if os.path.exists(output_path):
            print(f"Video {output_path} đã tồn tại, bỏ qua...")
            return

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        h, w = self.frames[0].shape[:2]
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        for frame in self.frames:
            out.write(frame)
        out.release()
        print(f"Augmented video saved to {output_path}")


def process_videos(input_folder, output_folder):
    error_log = []
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

            output_files = {
                "rotation": os.path.join(output_class_path, f"{base_name}_rotation.mp4"),
                "flip": os.path.join(output_class_path, f"{base_name}_flip.mp4"),
                "speedup": os.path.join(output_class_path, f"{base_name}_speedup.mp4"),
                "dropout": os.path.join(output_class_path, f"{base_name}_dropout.mp4"),
            }

            if all(os.path.exists(path) for path in output_files.values()):
                print(f"Tất cả video augment của {video_file} đã tồn tại, bỏ qua...")
                continue

            try:
                augmenter = VideoAugmentation(video_path)
                
                if not os.path.exists(output_files["rotation"]):
                    augmenter.rotation(angle=10).save_video(output_files["rotation"])
                if not os.path.exists(output_files["flip"]):
                    augmenter.horizontal_flip().save_video(output_files["flip"])
                if not os.path.exists(output_files["speedup"]):
                    augmenter.change_speed(speed_factor=1.2).save_video(output_files["speedup"])
                if not os.path.exists(output_files["dropout"]):
                    augmenter.frame_dropout(drop_ratio=0.2).save_video(output_files["dropout"])

            except (ValueError, MemoryError, np.core._exceptions._ArrayMemoryError) as e:
                print(f"Lỗi với file {video_file}: {str(e)}")
                error_log.append(video_path)
                continue
    
    # Ghi danh sách các file lỗi vào error_log.txt
    if error_log:
        with open("error_log.txt", "w") as f:
            for error_file in error_log:
                f.write(error_file + "\n")
        print("Danh sách file lỗi đã được lưu vào error_log.txt")

def process_error_video(input_folder, output_folder, error_file):
    error_log = []
    
    # Tạo thư mục output nếu chưa tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Đọc danh sách video bị lỗi từ error_file
    with open(error_file, "r") as f:
        error_files = set(f.read().splitlines())  # Dùng set để tìm nhanh hơn

    # Duyệt qua tất cả các thư mục lớp trong input_folder
    for class_folder in os.listdir(input_folder):
        class_path = os.path.join(input_folder, class_folder)
        output_class_path = os.path.join(output_folder, class_folder)

        if not os.path.isdir(class_path):
            continue  # Bỏ qua nếu không phải thư mục

        # Tạo thư mục output cho từng class nếu chưa tồn tại
        if not os.path.exists(output_class_path):
            os.makedirs(output_class_path)

        # Duyệt qua từng file trong class_folder
        for video_file in os.listdir(class_path):
            if video_file not in error_files:
                continue  # Bỏ qua nếu file không nằm trong danh sách lỗi
            
            video_path = os.path.join(class_path, video_file)
            output_files = {
                "rotation": os.path.join(output_class_path, f"{video_file}_rotation.mp4"),
                "flip": os.path.join(output_class_path, f"{video_file}_flip.mp4"),
                "speedup": os.path.join(output_class_path, f"{video_file}_speedup.mp4"),
                "dropout": os.path.join(output_class_path, f"{video_file}_dropout.mp4"),
            }

            # Kiểm tra nếu tất cả video augment đã tồn tại, thì bỏ qua
            if all(os.path.exists(path) for path in output_files.values()):
                print(f"Tất cả video augment của {video_file} đã tồn tại, bỏ qua...")
                continue

            try:
                augmenter = VideoAugmentation(video_path)
                
                if not os.path.exists(output_files["rotation"]):
                    augmenter.rotation(angle=10).save_video(output_files["rotation"])
                if not os.path.exists(output_files["flip"]):
                    augmenter.horizontal_flip().save_video(output_files["flip"])
                if not os.path.exists(output_files["speedup"]):
                    augmenter.change_speed(speed_factor=1.2).save_video(output_files["speedup"])
                if not os.path.exists(output_files["dropout"]):
                    augmenter.frame_dropout(drop_ratio=0.2).save_video(output_files["dropout"])

            except (ValueError, MemoryError, np.core._exceptions._ArrayMemoryError) as e:
                print(f"Lỗi với file {video_file}: {str(e)}")
                error_log.append(video_path)

    # Ghi lại danh sách file vẫn lỗi sau khi thử lại
    if error_log:
        with open(error_file, "w") as f:
            f.write("\n".join(error_log))

if __name__ == "__main__":
    input_path = os.path.join(os.getcwd(), "data", "raw_video", "private_data", "train")
    output_path = os.path.join(os.getcwd(), "data", "processed_video", "private_data", "train")
    error_file = os.path.join(os.getcwd(),"error" ,"error_log.txt")
    if error_file:
        process_error_video(input_path, output_path, error_file)
    else:
        process_videos(input_path, output_path)