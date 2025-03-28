import os
import shutil
import config
from utils import normalize_string, get_members_from_db

# # code for db
# def format_videos(directory):
#     """Đổi tên và tổ chức video vào thư mục chuẩn"""
#     output_folder = os.path.join(directory, "all_videos")
#     os.makedirs(output_folder, exist_ok=True)
#     members_dict = get_members_from_db()
#     for filename in os.listdir(directory):
#         if filename.endswith(".mp4"):
#             parts = filename.split("_")
#             if len(parts) == 4:
#                 continue  # File đã đúng format
#             for id_, name in members_dict.items():
#                 if normalize_string(name) in normalize_string(filename):
#                     new_filename = f"{config.DEVICE_ID}_{id_}_{name}_{parts[-1]}"
#                     shutil.move(os.path.join(directory, filename), os.path.join(output_folder, new_filename))
#                     print(f"✅ Đã chuyển & đổi tên: {filename} ➝ {new_filename}")
#                     break

# code step-by-step
def format_videos(base_directory, output_directory = r'D:\FPT\CN9\Thesis\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\data\private_data\all_videos'):
    """
    Đổi tên file video và đưa tất cả vào thư mục chung với format:
    [id thiết bị]_[id]_[Hovaten]_[Tendongtac].mp4
    """
    os.makedirs(output_directory, exist_ok=True)  # Tạo thư mục đích nếu chưa có

    for device_folder in os.listdir(base_directory):
        device_path = os.path.join(base_directory, device_folder)

        if not os.path.isdir(device_path):  # Bỏ qua nếu không phải thư mục
            continue

        # 1️⃣ Lấy ID thiết bị từ config
        device_id = config.DEVICE_ID.get(device_folder)  # Nếu không tìm thấy ID, gán mặc định "00"

        for action_folder in os.listdir(device_path):
            action_path = os.path.join(device_path, action_folder)

            if not os.path.isdir(action_path):  # Bỏ qua nếu không phải thư mục
                continue

            for filename in os.listdir(action_path):
                file_path = os.path.join(action_path, filename)

                if not filename.endswith(".mp4"):  # Chỉ xử lý file video
                    continue

                # 2️⃣ Kiểm tra format file cũ [id]_[Hovaten]_[Tendongtac].mp4
                parts = filename.split("_")
                if len(parts) < 3:
                    print(f"⚠️ Bỏ qua file '{filename}' vì không đúng format.")
                    continue

                student_id = parts[0]
                student_name = parts[1]
                action_name = parts[2].replace(".mp4", "")

                # 3️⃣ Format lại tên mới [id thiết bị]_[id]_[Hovaten]_[Tendongtac].mp4
                new_filename = f"{device_id}_{student_id}_{student_name}_{action_name}.mp4"
                new_path = os.path.join(output_directory, new_filename)

                # 4️⃣ Di chuyển file
                try:
                    shutil.move(file_path, new_path)
                    print(f"✅ Đã chuyển & đổi tên: {filename} ➝ {new_filename}")
                except Exception as e:
                    print(f"❌ Lỗi khi di chuyển {filename}: {e}")