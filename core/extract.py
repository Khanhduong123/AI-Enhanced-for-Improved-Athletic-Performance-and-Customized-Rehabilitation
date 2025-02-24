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
        else:
            frame_keypoints["pose"] = {kp: [0, 0, 0] for kp in keypoint_names}  # Nếu không nhận diện được, gán 0

        skeleton_data.append(frame_keypoints)

    cap.release()

    with open(output_json, "w") as f:
        json.dump(skeleton_data, f, indent=4)

def process_videos(video_folder, output_folder, fps=10):
    if not os.path.exists(video_folder):
        print(f"Error: Video folder '{video_folder}' not found.")
        return
    
    class_folders = [folder for folder in os.listdir(video_folder) if os.path.isdir(os.path.join(video_folder, folder))]
    # class_folders =['Garland_Pose']
    if not class_folders:
        print("No class folders found in the dataset.")
        return

    for class_name in class_folders:
        class_path = os.path.join(video_folder, class_name)
        output_class_folder = os.path.join(output_folder, class_name)
        os.makedirs(output_class_folder, exist_ok=True)

        video_files = [f for f in os.listdir(class_path) if f.endswith((".mp4", ".avi", ".mov"))]
        #Thứ tự extract video.
        #['sample1.mp4', 'sample10.mp4', 'sample11.mp4', 'sample12.mp4', 'sample13.mp4', 'sample14.mp4', 'sample15.mp4', 'sample16.mp4', 'sample17.mp4', 'sample18.mp4', 'sample19.mp4', 'sample2.mp4', 'sample20.mp4', 'sample21.mp4', 'sample22.mp4', 'sample23.mp4', 'sample24.mp4', 'sample25.mp4', 'sample3.mp4', 'sample4.mp4', 'sample5.mp4', 'sample6.mp4', 'sample7.mp4', 'sample8.mp4', 'sample9.mp4']
        for video_file in video_files:
            video_path = os.path.join(class_path, video_file)
            output_json = os.path.join(output_class_folder, f"{os.path.splitext(video_file)[0]}.json")
            action_name = os.path.splitext(video_file)[0]  # Lấy tên video làm tên động tác

            print(f"📌 Processing {video_file} in class {class_name}...")
            extract_skeleton_with_selected_frames(video_path, output_json, fps, action_name)

if __name__ == "__main__":   
    video_folder = "../data/raw_video"
    output_folder = "../data/keypoints"
    fps = 10  # Frame per second

    process_videos(video_folder, output_folder, fps)