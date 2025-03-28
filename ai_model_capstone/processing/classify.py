import os
import shutil
import config

def move_videos(directory):
    """Di chuyển video vào thư mục theo bài tập"""
    for filename in os.listdir(directory):
        if filename.endswith(".mp4"):
            parts = filename.split("_")
            if len(parts) >= 3:
                category = parts[3].replace(".mp4", "")
                destination_folder = os.path.join(directory, category)
                os.makedirs(destination_folder, exist_ok=True)
                shutil.move(os.path.join(directory, filename), os.path.join(destination_folder, filename))
                print(f"✅ Đã di chuyển: {filename} ➝ {destination_folder}")
