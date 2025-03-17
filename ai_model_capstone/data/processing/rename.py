import os
import config
from utils import normalize_string, get_members_from_db

# # code for db
# def rename_videos(directory):
#     """Đổi tên file theo format [ID]_[Tên]_[ĐộngTác].mp4"""
#     members_dict = get_members_from_db()
#     for filename in os.listdir(directory):
#         old_path = os.path.join(directory, filename)
#         if filename.endswith(".mp4"):
#             parts = filename.split("_")
#             if len(parts) < 3:
#                 normalized_filename = normalize_string(os.path.splitext(filename)[0])
#                 for id_, name in members_dict.items():
#                     if normalize_string(name) in normalized_filename:
#                         new_filename = f"{id_}_{name}_{parts[-1]}.mp4"
#                         new_path = os.path.join(directory, new_filename)
#                         os.rename(old_path, new_path)
#                         print(f"✅ Đã đổi tên: {filename} ➝ {new_filename}")
#                         break

# code for rename step-by-step
GLOBAL_NAME_DICT = {
    "01": "LePhanTheVinh",
    "02": "NguyenCatTuong",
    "03": "VuDucThienDung",
    "04": "NguyenNgocNhuThao",
    "05": "HoangVanLong",
    "06": "VoLeThanhTuyen",
    "07": "LuongHoangTrucVan",
    "08": "DoanVanNghia",
    "09": "NguyenDaoKimUyen",
    "10": "TranVietDangKhoa",
    "11": "TranCongQuangLong",
    "12": "NguyenLamSon",
    "13": "LeTanKha"
}
def rename_videos(base_directory):
    """
    Đổi tên file video trong các thư mục động tác theo format [ID]_[HovaTen]_[Tendongtac].mp4
    """
    for action_folder in os.listdir(base_directory):
        action_path = os.path.join(base_directory, action_folder)

        if not os.path.isdir(action_path):  # Bỏ qua nếu không phải thư mục
            continue
        
        for filename in os.listdir(action_path):
            file_path = os.path.join(action_path, filename)

            if not filename.endswith(".mp4"):  # Chỉ xử lý file video
                continue

            filename_without_ext, ext = os.path.splitext(filename)
            normalized_filename = normalize_string(filename_without_ext)

            # 2️⃣ Tìm ID của thí sinh dựa trên tên file
            member_id = None
            member_name = None
            for id_, name in GLOBAL_NAME_DICT.items():
                if normalize_string(name) in normalized_filename:
                    member_id = id_
                    member_name = name
                    break

            if member_id is None:
                print(f"⚠️ Bỏ qua file '{filename}' vì không tìm thấy ID phù hợp.")
                continue

            # 3️⃣ Định dạng tên mới
            new_filename = f"{member_id}_{member_name}_{action_folder}{ext}"
            new_path = os.path.join(action_path, new_filename)

            # 4️⃣ Đổi tên file
            try:
                os.rename(file_path, new_path)
                print(f"✅ Đã đổi tên: {filename} ➝ {new_filename}")
            except Exception as e:
                print(f"❌ Lỗi khi đổi tên {filename}: {e}")

