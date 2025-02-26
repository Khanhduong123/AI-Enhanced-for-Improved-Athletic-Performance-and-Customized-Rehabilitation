import os
import json
import numpy as np

def load_json(json_path):
    """ Đọc dữ liệu keypoints từ file JSON. """
    with open(json_path, "r") as file:
        return json.load(file)

def save_json(data, output_path):
    """ Lưu dữ liệu JSON đã được xử lý. """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)
    print(f"✅ JSON saved: {output_path}")

def json_to_numpy(json_data):
    """ Chuyển đổi dữ liệu từ JSON thành numpy array (T, 33, 3). """
    keypoints = []
    for frame in json_data:
        frame_data = []
        for key in frame["pose"]:
            frame_data.append(frame["pose"][key])
        keypoints.append(frame_data)
    return np.array(keypoints)  # (T, 33, 3)

def numpy_to_json(numpy_data, original_json):
    """ Chuyển đổi numpy array trở lại JSON format. """
    new_json = []
    for i, frame in enumerate(original_json):
        new_frame = {
            "frame": frame["frame"],
            "name": frame["name"],
            "pose": {}
        }
        for j, key in enumerate(frame["pose"].keys()):
            new_frame["pose"][key] = numpy_data[i][j].tolist()
        new_json.append(new_frame)
    return new_json
