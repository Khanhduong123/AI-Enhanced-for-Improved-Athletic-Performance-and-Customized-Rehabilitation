import cv2
import mediapipe as mp
import os

def extract_skeleton_from_video(input_video_path, output_video_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        cv2.imshow("Skeleton Extraction", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        out.write(frame)
        
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Skeleton-extracted video saved at: {output_video_path}")

def main():
    extract_skeleton_from_video(r"D:\Thesis_SP25\work\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\data\processed_video\public_data\val\Garland_Pose\sample21.mp4", 'skeleton.mp4')

if __name__ == "__main__":
    main()