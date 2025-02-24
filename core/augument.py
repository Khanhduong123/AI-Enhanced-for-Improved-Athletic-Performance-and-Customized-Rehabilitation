import cv2
import numpy as np
import os
import mediapipe as mp
import json
class Augumentation:
    def __init__(self, skeleton):
        self.skeleton = skeleton
    
    def jittering(self, noise_level=0.01):
        """
        1. JITTERING (thêm nhiễu vào các keypoints)
            - Thêm nhiễu guassian (norm distribution) vào các keypoints
            - giúp mô hình không bị phụ thuộc vào vị trí chính xác của keypoints
            - giúp mô hình học được các biến thể của keypoints
            - công thức: skeleton(aug) = skeleton + N(0, sigma^2) với N(0, sigma^2) là phân phối Guassian có trung bình 0 và độ lệch chuẩn sigma
            - Dùng khi nào? Khi muốn mô hình học được sự biến đổi nhỏ trong tọa độ keypoints, khi dữ liệu quá sạch và dễ bị overfitting
            - VD: ban đầu: (0.5, 0.3, 0.2) --> jittering (với noise nhỏ): (0.502, 0.295, 0.205)
        """
        noise = np.random.normal(loc=0, scale=noise_level, size=self.skeleton.shape)
        return self.skeleton + noise
    

    def scaling(self, scale_range=(0.9, 1.1)):
        """
        Scaling (phóng to/ thu nhỏ toàn bộ skeleton)
            - Phóng to hoặc thu nhỏ keypoints theo một hệ số ngẫu nhiên.
            - Giúp mô hình không bị phụ thuộc vào kích thước người tập yoga.
            - Công thức: skeleton(aug) = skeleton * scale_factor (trong này set là trong khoảng 0.9 và 1.1)
            - Dùng khi nào? Khi muốn mô hình học được sự biến đổi về kích thước của người tập yoga (cao thấp, mập ốm,...) --> không bị ảnh hưởng bởi kích thước tuyệt đối
            - VD: ban đầu: (0.5, 0.3, 0.2) --> scaling (scale_factor = 1.1): (0.55, 0.33, 0.22)
        """
        scale_factor = np.random.uniform(scale_range[0], scale_range[1])
        return self.skeleton * scale_factor
    
    def rotation(self, angle_range=(-15, 15)):
        """
        Rotation (Xoay toàn bộ skeleton quanh trung tâm)
        - Xoay khung xương quanh trung tâm theo góc ngẫu nhiên (-15 đến 15 độ)
        - Giúp mô hình hiểu được các tư thế nhìn từ nhiều góc độ khác nhau.
        - Công thức: 
            * R = [[cos(theta), -sin(theta)], [sin(theta), cos(theta)]] với theta là góc xoay
            * skeleton(aug) = R * (skeleton - center)*R + center
        - Dùng khi nào? Khi muốn mô hình học được sự biến đổi về góc nhìn của người tập yoga, phòng khi data chỉ thu được từ một góc độ cố định
        """

        angle = np.radians(np.random.uniform(angle_range[0], angle_range[1]))
        cos_val, sin_val = np.cos(angle), np.sin(angle)

        # Tạo ma trận xoay
        rotation_matrix = np.array([[cos_val, -sin_val], [sin_val, cos_val]])

        #chỉ xoay x, y (không xoay z)
        self.skeleton[:, :, :2] = np.dot(self.skeleton[:, :, :2] - np.mean(self.skeleton[:, :, :2], axis=0), rotation_matrix) + np.mean(self.skeleton[:, :, :2], axis=0) 

        return self.skeleton

    def horizontal_flip(self):
        """
        Horizontal Flip (Lật keypoints trái/phải)
            - Lật toàn bộ tư thế theo trục X
            - Giúp mô hình hiểu cả tư thế từ cả hai phía trái phải của cùng một động tác
            - công thức: skeleton(aug) = [:, :, 0] = 1 - skeleton[:, :, 0]
            - Dùng khi nào? Khi muốn mô hình học được sự biến đổi về trái phải của người tập yoga, khi dữ liệu chỉ có một phiên bản của động tác
            - VD: ban đầu (0.2, 0.5) --> flip (0.8, 0.5)
        """
        self.skeleton[:, :, 0] = 1 - self.skeleton[:, :, 0]
        return self.skeleton
    
    def temporal_warping(self, warp_factor_range=(0.8,1.2)):
        """
        Tăng/Giảm tốc độ chuyển động)
            - Tăng hoặc giảm tốc độ của video mà không làm mất động tác.
            - Giúp mô hình hiểu được động tác thực hiện nhanh/chậm khác nhau.
            - công thức: 
                * num_frames = T * warp_factor
                * skeleton(aug) = skeleton[indices]
                * với warp_factor (0.8, 1.2) là hệ số tốc độ, indices là các chỉ số của frame sau khi tăng/giảm tốc độ
            - Dùng khi nào? Khi động tác có thể thực hiện với tốc độ khác nhau, khi video có frame_rate không đồng đều
            - VD: ban đầu: 10 frames --> giảm tốc độ (warp_factor = 1.2): 12 frames
        """
        warp_factor = np.random.uniform(warp_factor_range[0], warp_factor_range[1])
        num_frames = int(self.skeleton.shape[0] * warp_factor)
        indices = np.linspace(0, self.skeleton.shape[0] - 1, num_frames, dtype=int)
        return self.skeleton[indices]
    
    def time_masking(self, mask_ratio=0.2):
        """
        Time Masking (Ẩn một số frame)
            - Loại bỏ một số frame ngẫu nhiên, giả lập video bị mất frame hoặc hành động không liên tục.
            - Giúp mô hình học cách đối phó với dữ liệu không liên tục.
            - Dùng khi nào? Khi video có tốc độ ghi hình không ổn định, khi muốn mô hình không bị phụ thuộc vào toàn bộ chuỗi frame.
            - VD: ban đầu: [F1, F2, F3, F4, F5] --> Sau masking: [F1, 0, F3, 0, F5]

        """
        T = self.skeleton.shape[0]
        num_mask = int(T * mask_ratio)
        mask_indices = np.random.choice(T, num_mask, replace=False)
        self.skeleton[mask_indices] = 0  # Gán toàn bộ frame đó về 0
        return self.skeleton
    
    def frame_interpolation(self):
        """
        Frame Interpolation(Nội suy khung hình)
            - Tạo thêm frame nội suy giữa các frame thực tế, giúp mô hình học mượt hơn.
            - Giả lập dữ liệu có tốc độ quay cao hơn.
            - Dùng khi nào? Khi video bị ít frame, cần tạo thêm frame để training, khi muốn mô hình học được chuyển động mượt mà hơn.
            - VD: ban đầu: [F1, F2, F3] --> Interpolation: [F1, F1.5, F2, F2.5, F3]
        """
        T, V, C = self.skeleton.shape
        new_T = T * 2 - 1  # Tăng gấp đôi số frame
        interpolated_skeleton = np.zeros((new_T, V, C))

        for i in range(T - 1):
            interpolated_skeleton[2 * i] = self.skeleton[i]
            interpolated_skeleton[2 * i + 1] = (self.skeleton[i] + self.skeleton[i + 1]) / 2  # Nội suy
        
        interpolated_skeleton[-1] = self.skeleton[-1]
        return interpolated_skeleton
    
    @staticmethod
    def flip_keypoints_xy(input_json, output_json):
        """
        Đọc file JSON, lật keypoints theo trục X và Y, sau đó lưu lại file mới.
        """
        # Đọc dữ liệu từ file JSON
        with open(input_json, "r") as file:
            data = json.load(file)

        flipped_data = []
        
        for frame in data:
            flipped_frame = frame.copy()
            flipped_frame["pose"] = {
                key: [1 - value[0], 1 - value[1]]  # Lật cả x và y
                for key, value in frame["pose"].items()
            }
            flipped_data.append(flipped_frame)

        # Lưu dữ liệu mới vào file JSON
        with open(output_json, "w") as file:
            json.dump(flipped_data, file, indent=4)

        print(f"Keypoints flipped and saved to {output_json}")

if __name__ == "__main__":
    pass