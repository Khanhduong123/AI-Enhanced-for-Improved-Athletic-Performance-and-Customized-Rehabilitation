import os
import torch
import numpy as np
import cv2
import mediapipe as mp
import sys
import csv
import traceback
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.model import SPOTER, YogaGCN
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def load_model(model_path, model_name, num_classes):
    if model_name == "spoter":
        model = SPOTER(hidden_dim=72, num_classes=num_classes, max_frame=100, num_heads=9, encoder_layers=1, decoder_layers=1)
    elif model_name == "gcn":
        model = YogaGCN(in_channels=3, hidden_dim=128, num_classes=num_classes)
    else:
        raise ValueError(f"No matching model found for {model_name}")
    checkpoint = torch.load(model_path, map_location=torch.device("cpu"))
    if "model" in checkpoint:
        model.load_state_dict(checkpoint["model"], strict=False)
    else:
        model.load_state_dict(checkpoint, strict=False)
    model.eval()
    return model

def extract_skeleton_from_video(video_path, max_frames=100, fps=10):
    """Trích xuất keypoints từ video với FPS là 10."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Không thể mở video: {video_path}")

    # Lấy FPS thực tế của video
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        raise ValueError(f"Video {video_path} không có frame nào!")

    # Giảm FPS xuống 10
    step = int(video_fps // fps)  # Tính bước nhảy (số frame cần bỏ qua)
    indices = np.arange(0, total_frames, step=step)  # Lấy các frame có chỉ số chia hết cho bước nhảy

    # Giới hạn số frame tối đa nếu số frame quá nhiều
    indices = indices[:max_frames]  # Đảm bảo chỉ lấy tối đa max_frames frame

    skeleton_data = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            print(f"Không thể đọc frame {idx}")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        keypoints = []
        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                keypoints.append([lm.x, lm.y, lm.z])

        # Đảm bảo luôn có 33 keypoints
        if len(keypoints) != 33:
            keypoints = [[0, 0, 0]] * 33

        skeleton_data.append(keypoints)

    cap.release()
    skeleton_data = np.array(skeleton_data)  # Shape: (num_frames, 33, 3)

    if skeleton_data.shape[1] != 33:
        raise ValueError(f"Keypoints không đúng! Current size: {skeleton_data.shape}")

    return skeleton_data

def normalize_skeleton(skeleton):
    if skeleton.size == 0:
        raise ValueError("Empty skeleton")
    mean_pose = np.mean(skeleton[:, :, :2], axis=(0, 1))
    skeleton[:, :, :2] -= mean_pose
    return skeleton

def get_edge_index():
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 7),
        (0, 4), (4, 5), (5, 6), (6, 8),
        (9, 10), (11, 12),
        (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
        (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
        (11, 23), (12, 24), (23, 24),
        (23, 25), (25, 27), (27, 29), (27, 31), (29, 31),
        (24, 26), (26, 28), (28, 30), (28, 32), (30, 32)
    ]
    return torch.tensor(edges, dtype=torch.long).t().contiguous()

def predict_action(video_path, model, model_name, classes):
    skeleton = extract_skeleton_from_video(video_path)
    skeleton = normalize_skeleton(skeleton)
    skeleton_tensor = torch.tensor(skeleton, dtype=torch.float32)

    with torch.no_grad():
        if model_name == 'spoter':
            num_frames, num_keypoints, keypoint_dim = skeleton_tensor.shape
            skeleton_tensor = skeleton_tensor.view(1, -1)
            outputs = model(skeleton_tensor)
        else:
            num_frames, num_keypoints, keypoint_dim = skeleton_tensor.shape
            skeleton_tensor = skeleton_tensor.view(num_frames * num_keypoints, keypoint_dim)
            batch = torch.zeros(num_frames * num_keypoints, dtype=torch.long)
            edge_index = get_edge_index()
            outputs = model(skeleton_tensor, edge_index, batch)

        probs = torch.nn.functional.softmax(outputs, dim=1)
        preds = probs.argmax(dim=1).item()
        confidence_score = probs.max(dim=1)[0].item()
    return classes[preds], confidence_score

def save_confusion_matrix(y_true, y_pred, labels, output_path):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    fig, ax = plt.subplots(figsize=(8, 6))
    disp.plot(ax=ax, cmap=plt.cm.Blues, xticks_rotation=45, colorbar=False)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    data_dir = "test/Oppo"
    os.makedirs("result/csv", exist_ok=True)
    os.makedirs("result/img", exist_ok=True)
    os.makedirs("error", exist_ok=True)
    

    run_counts = [1]
    CLASS_LABELS = ["Dangchanraxanghiengminh", "Ngoithangbangtrengot", "Sodatvuonlen", "Xemxaxemgan"]
    model_name = "gcn" # "spoter" 

    if model_name == "spoter":
        model_path = "checkpoints/method_2/finetune_spoter_method_2_1enc_1dec_72hu_30eps_0_00001lr.pt"
    else:
        model_path = "/checkpoints/method_2/finetune_gcn_method_2_4layers_128hu_50eps_0_001lr.pt"

    model = load_model(model_path, model_name, num_classes=len(CLASS_LABELS))

    for count in run_counts:
        output_csv = f"result/csv/{model_name}_run_method2_{count}_times.csv"
        log_file_path = f"error/{model_name}_run_method2_{count}_times_log_error.txt"
        y_true_all = []
        y_pred_all = []

        with open(output_csv, mode="w", newline="") as file, open(log_file_path, mode="a") as log_file:
            writer = csv.writer(file)
            writer.writerow(["Video Name", "Predicted Class", "Actual Class", "Confidence Score", "Correct", "Model", "Run Count"])

            for _ in range(count):
                for class_name in os.listdir(data_dir):
                    class_path = os.path.join(data_dir, class_name)
                    if not os.path.isdir(class_path):
                        continue

                    for file_name in os.listdir(class_path):
                        if not file_name.endswith(".mp4"):
                            continue
                        video_path = os.path.join(class_path, file_name)
                        try:
                            print(f"Processing {video_path} with {model_name}... Run {count}...")
                            predicted_class, confidence = predict_action(video_path, model, model_name, CLASS_LABELS)
                            is_correct = (predicted_class == class_name)
                            writer.writerow([file_name, predicted_class, class_name, confidence, is_correct, model_name, count])
                            y_true_all.append(class_name)
                            y_pred_all.append(predicted_class)
                        except Exception as e:
                            error_msg = f"[ERROR] Video: {video_path}\n{traceback.format_exc()}\n"
                            print(error_msg)
                            log_file.write(error_msg)

        cm_output_path = f"result/img/{model_name}_run_method2_{count}_times_confusion_matrix.png"
        save_confusion_matrix(y_true_all, y_pred_all, CLASS_LABELS, cm_output_path)
        print(f"=> Đã lưu confusion matrix tại: {cm_output_path}")


if __name__ == "__main__":
    main()
