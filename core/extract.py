import os
import cv2
import json
import numpy as np
import mediapipe as mp

def extract_skeleton_with_selected_frames(video_path, output_json, fps, action_name):
    if not os.path.exists(os.path.dirname(output_json)):
        os.makedirs(os.path.dirname(output_json))

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

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
    selected_frames = np.arange(0, total_frames, step=int(video_fps // fps), dtype=int)

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
        else:
            frame_keypoints["pose"] = {kp: [0, 0, 0] for kp in keypoint_names}  # Gán 0 nếu không nhận diện được

        skeleton_data.append(frame_keypoints)

    cap.release()

    with open(output_json, "w") as f:
        json.dump(skeleton_data, f, indent=4)

def process_videos(video_root_folder, output_root_folder, fps=10):
    if not os.path.exists(video_root_folder):
        print(f"⚠️ Warning: Folder '{video_root_folder}' not found.")
        return

    subfolders = [os.path.join(video_root_folder, cls) for cls in os.listdir(video_root_folder) if os.path.isdir(os.path.join(video_root_folder, cls))]
    # print(subfolders)
    # subfolders = ['D:\\MinhHoang\\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\\data\\processed_video\\public_data\\train\\Lunge_Pose']

    for class_path in subfolders:
        class_name = os.path.basename(class_path)
        output_class_folder = os.path.join(output_root_folder, class_name)
        os.makedirs(output_class_folder, exist_ok=True)

        video_files = [f for f in os.listdir(class_path) if f.endswith((".mp4", ".avi", ".mov"))]
        # print(video_files)
        
        # video_files= ['sample6.mp4', 'sample7.mp4']
        for video_file in video_files:
            try:
                video_path = os.path.join(class_path, video_file)
                output_json = os.path.join(output_class_folder, f"{os.path.splitext(video_file)[0]}.json")
                action_name = os.path.splitext(video_file)[0]  # Lấy tên video làm tên động tác

                # Nếu file JSON đã tồn tại, bỏ qua
                if os.path.exists(output_json):
                    print(f"✅ Skipping {video_file} (Already processed)")
                    continue

                print(f"📌 Processing {video_file} in class {class_name}...")
                extract_skeleton_with_selected_frames(video_path, output_json, fps, action_name)
            except Exception as e:
                print(f"❌ Error processing file {video_file}: {e}")
            

if __name__ == "__main__":
    video_root_folder = os.path.join(os.getcwd(), "data", "processed_video", "public_data", "train")
    output_root_folder = os.path.join(os.getcwd(), "data", "keypoints", "public_data", "train")
    process_videos(video_root_folder, output_root_folder)