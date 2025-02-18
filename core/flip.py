import json
import os

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

    print(f"✅ Keypoints flipped and saved to {output_json}")

def main():
    input_folder = "output_json"  # Thư mục chứa file JSON gốc
    flipped_folder = "flipped_json"  # Thư mục lưu file JSON sau khi lật
    os.makedirs(flipped_folder, exist_ok=True)

    # Tìm tất cả file JSON trong thư mục đầu vào
    json_files = [f for f in os.listdir(input_folder) if f.endswith(".json")]

    if not json_files:
        print("❌ No JSON files found in the folder.")
        return

    for json_file in json_files:
        input_json = os.path.join(input_folder, json_file)
        output_json = os.path.join(flipped_folder, f"flipped_{json_file}")

        print(f"Processing {json_file}...")
        flip_keypoints_xy(input_json, output_json)

if __name__ == "__main__":
    main()
