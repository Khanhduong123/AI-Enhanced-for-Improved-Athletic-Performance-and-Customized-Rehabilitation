import cv2
import mediapipe as mp
import numpy as np
import json
import os

def extract_skeleton_with_selected_frames(video_path, output_json, fps, action_name):
    if not os.path.exists(os.path.dirname(output_json)):
        os.makedirs(os.path.dirname(output_json))

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils  # Dùng để vẽ skeleton lên frame

    keypoint_names = [
        "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner",
        "right_eye", "right_eye_outer", "left_ear", "right_ear", "mouth_left",
        "mouth_right", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_pinky", "right_pinky", "left_index", "right_index",
        "left_thumb", "right_thumb", "left_hip", "right_hip", "left_knee", "right_knee",
        "left_ankle", "right_ankle", "left_heel", "right_heel", "left_foot_index", "right_foot_index"
    ]

    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    selected_frames = np.arange(0, total_frames, step=int(video_fps / fps), dtype=int)

    skeleton_data = []

    for idx in selected_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        frame_keypoints = {"frame": int(idx), "name": action_name, "pose": {}}
        
        if results.pose_landmarks:
            for i, lm in enumerate(results.pose_landmarks.landmark):
                frame_keypoints["pose"][keypoint_names[i]] = [lm.x, lm.y, lm.z]
            
            # Vẽ keypoints lên frame
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        else:
            frame_keypoints["pose"] = {kp: [0, 0, 0] for kp in keypoint_names}  # Nếu không nhận diện được, gán 0

        skeleton_data.append(frame_keypoints)

        # 📌 Hiển thị frame với keypoints
        cv2.imshow(f"Processing: {action_name}", frame)

        # Nhấn 'q' để thoát ngay lập tức, hoặc bất kỳ phím nào để tiếp tục
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()  # Đóng tất cả cửa sổ popup

    with open(output_json, "w") as f:
        json.dump(skeleton_data, f, indent=4)

def process_videos(video_folder, output_folder, fps=10):
    if not os.path.exists(video_folder):
        print(f"❌ Error: Video folder '{video_folder}' not found.")
        return
    
    class_folders = [folder for folder in os.listdir(video_folder) if os.path.isdir(os.path.join(video_folder, folder))]
    print(class_folders)
#     class_folders = ["Ngoithangbangtrengot"]

    if not class_folders:
        print("❌ No class folders found in the dataset.")
        return

    for class_name in class_folders:
        class_path = os.path.join(video_folder, class_name)
        output_class_folder = os.path.join(output_folder, class_name)
        os.makedirs(output_class_folder, exist_ok=True)

        video_files = [f for f in os.listdir(class_path) if f.endswith((".mp4", ".avi", ".mov"))]
        
        for video_file in video_files:
            video_path = os.path.join(class_path, video_file)
            output_json = os.path.join(output_class_folder, f"{os.path.splitext(video_file)[0]}.json")
            action_name = os.path.splitext(video_file)[0]  # Lấy tên video làm tên động tác

            print(f"📌 Processing {video_file} in class {class_name}...")
            extract_skeleton_with_selected_frames(video_path, output_json, fps, action_name)

if __name__ == "__main__":
    # Parameters   
    FPS = 10
    video_folder = "../data/raw_video"
    output_folder = "../data/keypoints"

    process_videos(video_folder, output_folder, FPS)
