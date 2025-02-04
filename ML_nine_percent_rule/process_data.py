import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# Danh sách các bộ phận cơ thể
BODY_PARTS = [
    "BODY",
    "FACE_NECK",
    "RIGHT_ARM",
    "LEFT_ARM",
    "RIGHT_LEG",
    "LEFT_LEG"
]

# Thư mục chứa dữ liệu pose (thay vì chỉ có 2, giờ hỗ trợ n thư mục)
SOURCE_DIRS = ["pose_data_csv1", "pose_data_csv2"]  # Thêm các thư mục mới tại đây
TARGET_DIR = "pose_data_csv"
KEYFRAME_FOLDERS = ["output_data1/keyframes", "output_data2/keyframes"]  # Thêm các thư mục mới tại đây

# Tạo thư mục đích nếu chưa tồn tại
os.makedirs(TARGET_DIR, exist_ok=True)

def merge_csv_files(part_name, source_dirs, target_dir):
    """
    Gộp dữ liệu từ các file CSV của cùng một bộ phận từ nhiều thư mục nguồn.
    """
    dataframes = []
    for src in source_dirs:
        file_path = os.path.join(src, f"{part_name}_coordinates.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            dataframes.append(df)
        else:
            print(f"Warning: {file_path} not found!")

    if dataframes:
        merged_df = pd.concat(dataframes, axis=0)
        output_path = os.path.join(target_dir, f"{part_name}_coordinates.csv")
        merged_df.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")
    else:
        print(f"No data found for {part_name}.")

def get_frame_counts(folders):
    """
    Đếm số lượng frame (keyframe) trong mỗi folder.
    """
    frame_counts = []
    for folder in folders:
        if os.path.exists(folder):
            count = len([f for f in os.listdir(folder) if f.endswith('.jpg')])
            frame_counts.append(count)
        else:
            print(f"Warning: {folder} not found!")
            frame_counts.append(0)  # Nếu folder không tồn tại, coi như không có frame
    return frame_counts

def label_data(file_path, frame_counts):
    """
    Thêm nhãn (label) cho dữ liệu. Label sẽ được gán tuần tự theo thứ tự frame_counts.
    """
    df = pd.read_csv(file_path)
    labels = []
    for i, count in enumerate(frame_counts):
        labels.extend([i] * count)  # Gán nhãn theo số thứ tự của video

    if len(labels) != len(df):
        print(f"Warning: Mismatch in label count ({len(labels)}) and data count ({len(df)}) in {file_path}")
        return

    df["label"] = labels
    df.to_csv(file_path, index=False)
    print(f"Labeled and saved: {file_path}")

def scale_coordinates(file_path, body_part):
    """
    Scale dữ liệu tọa độ x và y của bộ phận cơ thể
    """
    df = pd.read_csv(file_path)
    
    # Loại bỏ các cột chứa "z"
    df = df[[col for col in df.columns if 'z' not in col]]
    
    # Lấy các cột x và y
    df_x = df[[i for i in df.columns if "x" in i] + ["label"]]
    df_y = df[[i for i in df.columns if "y" in i] + ["label"]]
    
    # Tính min và max cho x và y
    mii_x = df_x.drop("label", axis=1).values.min(axis=1, keepdims=True)
    mii_y = df_y.drop("label", axis=1).values.min(axis=1, keepdims=True)
    mxx_x = df_x.drop("label", axis=1).values.max(axis=1, keepdims=True)
    mxx_y = df_y.drop("label", axis=1).values.max(axis=1, keepdims=True)
    
    # Scale x và y
    df_x = (df_x - mii_x) / (mxx_x - mii_x)
    df_y = (df_y - mii_y) / (mxx_y - mii_y)
    
    # Lưu lại dữ liệu đã scale
    for i in range(1, len(df_x.columns)-1):  # Bỏ qua cột label
        df[f'{body_part}_{i}_x'] = df_x[f'{body_part}_{i}_x']
        df[f'{body_part}_{i}_y'] = df_y[f'{body_part}_{i}_y']
    
    # Lưu lại file đã scale
    df.to_csv(f"./new_{body_part}_coordinates.csv", index=False)

def split_train_test(data_dir):
    """
    Chia dữ liệu thành tập train và test
    """
    # Đọc file dữ liệu đã được scale
    df = pd.read_csv(data_dir)
    
    # Lấy X (input) và y (label)
    X = df.drop(columns=["label"])
    y = df["label"]
    
    # Chia dữ liệu thành tập train và test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Lưu kết quả chia train/test vào file CSV
    X_train.to_csv(f"{data_dir.replace('.csv', '_train.csv')}", index=False)
    X_test.to_csv(f"{data_dir.replace('.csv', '_test.csv')}", index=False)
    y_train.to_csv(f"{data_dir.replace('.csv', '_train_labels.csv')}", index=False)
    y_test.to_csv(f"{data_dir.replace('.csv', '_test_labels.csv')}", index=False)
    
    print(f"Train and test split saved for {data_dir}")
    

# Merge các bộ dữ liệu từ nhiều thư mục nguồn
for part in BODY_PARTS:
    merge_csv_files(part, SOURCE_DIRS, TARGET_DIR)

# Gán nhãn cho dữ liệu
frame_counts = get_frame_counts(KEYFRAME_FOLDERS)
for part in BODY_PARTS:
    label_data(os.path.join(TARGET_DIR, f"{part}_coordinates.csv"), frame_counts)

# Scale dữ liệu
for part in BODY_PARTS:
    scale_coordinates(os.path.join(TARGET_DIR, f"{part}_coordinates.csv"), part)

# Chia dữ liệu thành tập train và test
for part in BODY_PARTS:
    split_train_test(f"./new_{part}_coordinates.csv")
