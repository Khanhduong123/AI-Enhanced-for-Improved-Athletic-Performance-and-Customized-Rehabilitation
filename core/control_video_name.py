import os
import unicodedata

# -----------------------------------------------
# **Bước 1: Đổi đuôi .MOV thành .MP4 nếu có**
# -----------------------------------------------
def convert_mov_to_mp4(file_path):
    """Đổi tên file .MOV thành .MP4"""
    new_path = os.path.splitext(file_path)[0] + ".mp4"
    try:
        os.rename(file_path, new_path)
        print(f"✅ Đã đổi tên: {os.path.basename(file_path)} ➝ {os.path.basename(new_path)}")
        return new_path  # Trả về đường dẫn mới sau khi đổi tên
    except Exception as e:
        print(f"❌ Lỗi khi đổi tên {file_path}: {e}")
        return file_path  # Trả lại file gốc nếu đổi tên thất bại

# -----------------------------------------------
# **Bước 2: Chuẩn hóa chuỗi để tìm tên đúng**
# -----------------------------------------------
def normalize_string(input_str):
    """Chuẩn hóa chuỗi: loại bỏ dấu tiếng Việt, xóa khoảng trắng, viết thường"""
    nfkd_str = unicodedata.normalize("NFKD", input_str)
    no_accents = "".join([c for c in nfkd_str if not unicodedata.combining(c)])
    return no_accents.replace(" ", "").lower()  # Xóa khoảng trắng và viết thường

# -----------------------------------------------
# **Bước 3: Đổi tên file video về format chuẩn**
# -----------------------------------------------
def rename_video(file_path, action, members_dict):
    """Đổi tên file video nếu chưa đúng format [id]_[Tên]_[ĐộngTác].mp4"""
    file_dir, filename = os.path.split(file_path)
    filename_without_ext, ext = os.path.splitext(filename)

    # Kiểm tra nếu file đã có format đúng
    parts = filename_without_ext.split("_")
    if len(parts) == 3 and parts[2] == action:
        print(f"✅ File '{filename}' đã đúng format, bỏ qua.")
        return

    # Chuẩn hóa tên file để tìm ID phù hợp
    normalized_filename = normalize_string(filename_without_ext)
    print(f"🔍 DEBUG: Kiểm tra file '{filename}' => '{normalized_filename}'")

    video_id = None
    for id_, name in members_dict.items():
        if normalize_string(name) in normalized_filename:
            video_id = id_
            break

    if video_id is None:
        print(f"⚠️ Bỏ qua file '{filename}' vì không tìm thấy ID phù hợp.")
        return

    # Định dạng tên mới
    new_filename = f"{video_id}_{members_dict[video_id]}_{action}{ext}"
    new_path = os.path.join(file_dir, new_filename)

    # Đổi tên file
    try:
        os.rename(file_path, new_path)
        print(f"✅ Đã đổi tên: {filename} ➝ {new_filename}")
    except Exception as e:
        print(f"❌ Lỗi khi đổi tên {filename}: {e}")

# -----------------------------------------------
# **Bước 4: Chạy tất cả trong main()**
# -----------------------------------------------
def main():
    # Dictionary mapping ID với tên thành viên (giữ nguyên format chuẩn)
    members_dict = {
        "9" : "Nguyễn Đào Kim Uyên",
        "10" : "Trần Viết Đăng Khoa",
        "11" : "Trần Công Quang Long"
    }

    # Thư mục gốc chứa các động tác
    root_folder = r"D:\FPT\CN9\Thesis\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\data\raw_video"  # 🛠 Thay đường dẫn phù hợp

    # Mapping tên thư mục thành động tác
    action_mapping = {
        "ĐỘNG TÁC 1 XEM XA XEM GẦN": "Xemxaxemgan",
        "ĐỘNG TÁC 2 NGỒI THĂNG BẰNG TRÊN GÓT": "Ngoithangbangtrengot",
        "ĐỘNG TÁC 3 DANG CHÂN RA XA NGHIÊNG MÌNH": "Dangchanraxanghiengminh",
        "ĐỘNG TÁC 4 SỜ ĐẤT VƯƠN LÊN": "Sodatvuonlen"
    }

    # **1️⃣ Duyệt qua từng thư mục động tác**
    for folder_name, action in action_mapping.items():
        action_path = os.path.join(root_folder, folder_name)

        if not os.path.exists(action_path):
            print(f"❌ Lỗi: Thư mục '{action_path}' không tồn tại!")
            continue

        for filename in os.listdir(action_path):
            file_path = os.path.join(action_path, filename)

            # **Nếu file có đuôi .MOV -> Đổi thành .MP4 trước**
            if filename.lower().endswith(".mov"):
                file_path = convert_mov_to_mp4(file_path)  # Cập nhật đường dẫn mới sau khi đổi tên

            # **Sau đó kiểm tra và đổi tên nếu chưa đúng format**
            rename_video(file_path, action, members_dict)

    print("🎉 Hoàn tất quá trình xử lý video!")

if __name__ == "__main__":
    main()
