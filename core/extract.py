import cv2
import mediapipe as mp
import json
import os

def extract_keypoints(video_path, output_json, candidate_name):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    keypoint_names = [
        "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner",
        "right_eye", "right_eye_outer", "left_ear", "right_ear", "mouth_left",
        "mouth_right", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_pinky", "right_pinky", "left_index", "right_index",
        "left_thumb", "right_thumb", "left_hip", "right_hip", "left_knee", "right_knee",
        "left_ankle", "right_ankle", "left_heel", "right_heel", "left_foot_index", "right_foot_index"
    ]

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Unable to open video file {video_path}")
        return
    
    data = []
    frame_idx = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            frame_data = {"frame": frame_idx, "name": candidate_name, "pose": {}}
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                frame_data["pose"][keypoint_names[i]] = [landmark.x, landmark.y, landmark.z]
            data.append(frame_data)
        
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()

    with open(output_json, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Keypoints saved to {output_json}")

def main():
    video_folder = "../data/raw_video"
    output_folder = "../data/keypoints"

    if not os.path.exists(video_folder):
        print(f"❌ Error: Video folder '{video_folder}' not found.")
        return
    else:
        print(f"📁 Processing videos in '{video_folder}'...")

    # Lấy danh sách folder class trong video_folder
    class_folders = [folder for folder in os.listdir(video_folder) if os.path.isdir(os.path.join(video_folder, folder))]

    if not class_folders:
        print("❌ No class folders found in the data folder.")
        return

    for class_name in class_folders:
        class_path = os.path.join(video_folder, class_name)
        output_class_folder = os.path.join(output_folder, class_name)
        os.makedirs(output_class_folder, exist_ok=True)  # Tạo folder output tương ứng với class
        
        print(f"📂 Processing class: {class_name}...")

        video_files = [f for f in os.listdir(class_path) if f.endswith((".mp4", ".avi", ".mov"))]
        
        if not video_files:
            print(f"⚠️ No video files found in '{class_path}'. Skipping...")
            continue

        for video_file in video_files:
            video_path = os.path.join(class_path, video_file)
            output_json = os.path.join(output_class_folder, f"{os.path.splitext(video_file)[0]}.json")
            candidate_name = os.path.splitext(video_file)[0]
            print(f"▶ Processing {video_file} in class {class_name}...")
            extract_keypoints(video_path, output_json, candidate_name)

if __name__ == "__main__":
    main()
