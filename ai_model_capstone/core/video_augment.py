import cv2
import numpy as np
import random
import os

class PublicVideoAugmentationMethod1:
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

class PublicVideoAugmentationMethod2:
    def __init__(self, video_path):
        self.video_path = video_path
        self.original_frames = self._load_video()
        self.frames = self.original_frames.copy()

    def _load_video(self):
        """ Load video và trích xuất các frame """
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            raise ValueError(f"Không thể mở video: {self.video_path}")

        frames = []
        target_size = (1080, 1920)  # OpenCV nhận (width, height)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
            frames.append(frame_resized)

        cap.release()

        if len(frames) == 0:
            raise ValueError(f"Không có frame nào được trích xuất từ video: {self.video_path}")
        
        frames_array = np.array(frames, dtype=np.uint8)
        print(f"Kích thước frame sau khi resize: {frames_array.shape}")  # Debug
        return frames_array

    def rotation(self, angle=15):
        self.reset_frames()
        h, w = self.frames[0].shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        self.frames = np.array([cv2.warpAffine(frame, M, (w, h)) for frame in self.frames], dtype=np.uint8)
        return self

    def horizontal_flip(self):
        self.reset_frames()
        self.frames = np.array([cv2.flip(frame, 1) for frame in self.frames], dtype=np.uint8)
        return self

    def change_speed(self, speed_factor=1.2):
        self.reset_frames()
        num_frames = int(len(self.frames) * speed_factor)
        indices = np.linspace(0, len(self.frames) - 1, num_frames, dtype=int)
        self.frames = self.frames[indices]
        return self

    def frame_dropout(self, drop_ratio=0.2):
        self.reset_frames()
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



class PrivateVideoAugmentation:
    def __init__(self, video_path):
        self.video_path = video_path
        self.original_frames = self._load_video()  # Lưu frames gốc
        self.frames = self.original_frames.copy()  # Bản sao để augment

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

    def reset_frames(self):
        """ Reset frames về trạng thái gốc trước khi augment """
        self.frames = self.original_frames.copy()

    def rotation(self, angle=15):
        self.reset_frames()  # Reset về frames gốc
        h, w = self.frames[0].shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        self.frames = np.array([cv2.warpAffine(frame, M, (w, h)) for frame in self.frames])
        return self

    def horizontal_flip(self):
        self.reset_frames()  # Reset về frames gốc
        self.frames = np.array([cv2.flip(frame, 1) for frame in self.frames])
        return self

    def change_speed(self, speed_factor=1.2):
        self.reset_frames()  # Reset về frames gốc
        num_frames = int(len(self.frames) * speed_factor)
        indices = np.linspace(0, len(self.frames) - 1, num_frames, dtype=int)
        self.frames = self.frames[indices]
        return self

    def frame_dropout(self, drop_ratio=0.2):
        self.reset_frames()  # Reset về frames gốc
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


def process_videos(input_folder, output_folder, is_method2):
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

            # Nếu tất cả augmentations đã tồn tại, bỏ qua file này
            if all(os.path.exists(path) for path in output_files.values()):
                print(f"Tất cả video augment của {video_file} đã tồn tại, bỏ qua...")
                continue

            try:
                # Chọn phương pháp augmentation phù hợp
                augmenter_public = PublicVideoAugmentationMethod2(video_path) if is_method2 else PublicVideoAugmentationMethod1(video_path)
                augmenter_private = PrivateVideoAugmentation(video_path)
                # augmenter_private = PublicVideoAugmentationMethod1(video_path)

                # Danh sách augmenter để lặp qua
                augmenters = [augmenter_public, augmenter_private]
                # augmenters = [augmenter_private]

                # Danh sách augmentations cần thực hiện
                augmentations = {
                    "rotation": lambda augmenter: augmenter.rotation(angle=10),
                    "flip": lambda augmenter: augmenter.horizontal_flip(),
                    "speedup": lambda augmenter: augmenter.change_speed(speed_factor=1.2),
                    "dropout": lambda augmenter: augmenter.frame_dropout(drop_ratio=0.2)
                }

                # Lặp qua từng augmenter (public/private) để chạy augmentation
                for augmenter in augmenters:
                    for aug_type, aug_function in augmentations.items():
                        if not os.path.exists(output_files[aug_type]):
                            try:
                                aug_function(augmenter).save_video(output_files[aug_type])
                            except Exception as e:
                                print(f"Lỗi khi augment {aug_type} trên file {video_path}: {str(e)}")
                                error_log.append(video_path)

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

def process_error_video(input_folder, output_folder, error_file, is_method2):
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
            base_name = os.path.splitext(video_file)[0]  # Lấy tên file không có đuôi .mp4

            output_files = {
                "rotation": os.path.join(output_class_path, f"{base_name}_rotation.mp4"),
                "flip": os.path.join(output_class_path, f"{base_name}_flip.mp4"),
                "speedup": os.path.join(output_class_path, f"{base_name}_speedup.mp4"),#slowdown
                "dropout": os.path.join(output_class_path, f"{base_name}_dropout.mp4"),
            }

            # Kiểm tra nếu tất cả video augment đã tồn tại, thì bỏ qua
            if all(os.path.exists(path) for path in output_files.values()):
                print(f"Tất cả video augment của {video_file} đã tồn tại, bỏ qua...")
                continue

            try:
                # Chọn phương pháp augmentation phù hợp
                augmenter_public = PublicVideoAugmentationMethod2(video_path) if is_method2 else PublicVideoAugmentationMethod1(video_path)
                augmenter_private = PrivateVideoAugmentation(video_path)

                # Danh sách augmenter để lặp qua
                augmenters = [augmenter_public, augmenter_private]

                # Danh sách augmentations cần thực hiện
                augmentations = {
                    "rotation": lambda augmenter: augmenter.rotation(angle=10),
                    "flip": lambda augmenter: augmenter.horizontal_flip(),
                    "speedup": lambda augmenter: augmenter.change_speed(speed_factor=1.2),
                    "dropout": lambda augmenter: augmenter.frame_dropout(drop_ratio=0.2)
                }

                # Lặp qua từng augmenter (public/private) để chạy augmentation
                for augmenter in augmenters:
                    for aug_type, aug_function in augmentations.items():
                        if not os.path.exists(output_files[aug_type]):
                            try:
                                aug_function(augmenter).save_video(output_files[aug_type])
                            except Exception as e:
                                print(f"Lỗi khi augment {aug_type} trên file {video_path}: {str(e)}")
                                error_log.append(video_path)

            except (ValueError, MemoryError, np.core._exceptions._ArrayMemoryError) as e:
                print(f"Lỗi với file {video_file}: {str(e)}")
                error_log.append(video_path)

    # Ghi lại danh sách file vẫn lỗi sau khi thử lại
    if error_log:
        with open(error_file, "w") as f:
            f.write("\n".join(error_log))
        print("Danh sách file lỗi đã được cập nhật trong error_file.txt")


def main():
    # Các biến cấu hình:
    IS_PRIVATE = False # True nếu là private data, False nếu là public data
    ERROR_FILE = True
    IS_METHOD2 = True # True nếu sử dụng phương pháp augmentation 2, False nếu sử dụng phương pháp augmentation 1, dùng cho bộ public

    data_type = "private_data" if IS_PRIVATE else "public_data" #Public_data
    # input_path = os.path.join(os.getcwd(), "data", "method_1", "raw_video", data_type, "val" if IS_PRIVATE else "val")
    # output_path = os.path.join(os.getcwd(), "data", "method_1", "processed_video", data_type, "val" if IS_PRIVATE else "val")
    
    input_path = "/raw_video/train"
    output_path = "/processed_video/train_method_1"
    
    # Xử lý video chính
    process_videos(input_path, output_path, is_method2=IS_METHOD2)

    # Nếu cần xử lý lỗi, chạy process_error_video()
    # if ERROR_FILE:
    #     error_file = os.path.join(os.getcwd(), "error", "error_log.txt")
    #     process_error_video(input_path, output_path, error_file, is_private=IS_PRIVATE)

if __name__ == "__main__":
    main()