import cv2
import numpy as np
import os
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import mediapipe as mp

def load_cnn_model():
    model = models.resnet18(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, 1)
    model = model.eval()
    return model

def preprocess_frame(frame):
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(frame).unsqueeze(0)

def extract_keyframes(video_path, output_folder, model, threshold=0.1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    keyframe_count = 0
    prev_score = None
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame_tensor = preprocess_frame(frame)
        with torch.no_grad():
            score = model(frame_tensor).item()
        
        if prev_score is None or abs(score - prev_score) > threshold:
            keyframe_count += 1
            keyframe_path = os.path.join(output_folder, f'keyframe_{keyframe_count:04d}.jpg')
            cv2.imwrite(keyframe_path, frame)
            prev_score = score
        
        frame_count += 1
    
    cap.release()
    print(f"Extracted {keyframe_count} keyframes from {frame_count} frames.")

def process_images_with_mediapipe(image_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    
    for image_name in os.listdir(image_folder):
        image_path = os.path.join(image_folder, image_name)
        image = cv2.imread(image_path)
        if image is None:
            continue
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        
        output_path = os.path.join(output_folder, image_name)
        cv2.imwrite(output_path, image)
    
    print(f"Processed images saved in {output_folder}")

# Example usage
video_path = "test2.mp4"
output_root = "output_data2"
keyframe_folder = os.path.join(output_root, "keyframes")
processed_folder = os.path.join(output_root, "processed_keyframes")

if not os.path.exists(output_root):
    os.makedirs(output_root)

model = load_cnn_model()
extract_keyframes(video_path, keyframe_folder, model)
process_images_with_mediapipe(keyframe_folder, processed_folder)
