import os
import unicodedata
import shutil

# -------------------------------
# **Bước 1: Chuẩn hóa chuỗi để so khớp tên**
# -------------------------------
def normalize_string(input_str):
    """Loại bỏ dấu tiếng Việt, chuyển về lowercase, xóa khoảng trắng"""
    nfkd_str = unicodedata.normalize("NFKD", input_str)
    no_accents = "".join([c for c in nfkd_str if not unicodedata.combining(c)])
    return no_accents.replace(" ", "").lower()

# -------------------------------
# **Bước 2: Đổi tên file video nếu chưa đúng format**
# -------------------------------
def rename_videos(root_folder, members_dict, device_dict, output_folder):
    """Duyệt toàn bộ thư mục và đổi tên file về format chuẩn, sau đó dồn vào 1 thư mục"""
    phone_brands = device_dict.keys()  # ['iPhone', 'Samsung', 'Oppo']
    actions = ["Dangchanraxanghiengminh", "Ngoithangbangtrengot", "Sodatvuonlen", "Xemxaxemgan"]  # Động tác

    # Tạo thư mục đích nếu chưa có
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Duyệt từng hãng điện thoại
    for brand in phone_brands:
        brand_path = os.path.join(root_folder, brand)

        if not os.path.exists(brand_path):
            print(f"❌ Lỗi: Thư mục '{brand_path}' không tồn tại!")
            continue

        # Duyệt từng động tác trong từng hãng điện thoại
        for action in actions:
            action_path = os.path.join(brand_path, action)

            if not os.path.exists(action_path):
                print(f"❌ Lỗi: Thư mục '{action_path}' không tồn tại!")
                continue

            # Duyệt từng file video trong thư mục động tác
            for filename in os.listdir(action_path):
                file_path = os.path.join(action_path, filename)

                # Bỏ qua file nếu không phải .mp4
                if not filename.endswith(".mp4"):
                    continue

                # Tách tên file, bỏ phần mở rộng
                filename_without_ext, ext = os.path.splitext(filename)

                # Kiểm tra nếu file đã đúng format
                parts = filename_without_ext.split("_")
                if len(parts) == 4 and parts[3] == action:
                    print(f"✅ File '{filename}' đã đúng format, bỏ qua.")
                    continue

                # Chuẩn hóa tên file để tìm ID phù hợp
                normalized_filename = normalize_string(filename_without_ext)

                video_id = None
                for id_, name in members_dict.items():
                    if normalize_string(name) in normalized_filename:
                        video_id = id_
                        break

                if video_id is None:
                    print(f"⚠️ Bỏ qua file '{filename}' vì không tìm thấy ID phù hợp.")
                    continue

                # Lấy ID thiết bị
                device_id = device_dict[brand]

                # Định dạng tên mới
                new_filename = f"{device_id}_{video_id}_{members_dict[video_id]}_{action}{ext}"
                new_path = os.path.join(output_folder, new_filename)

                # Kiểm tra nếu file đã tồn tại trong thư mục đích
                counter = 1
                while os.path.exists(new_path):
                    new_filename = f"{device_id}_{video_id}_{members_dict[video_id]}_{action}_copy{counter}{ext}"
                    new_path = os.path.join(output_folder, new_filename)
                    counter += 1

                # Di chuyển file vào thư mục đích với tên mới
                try:
                    shutil.move(file_path, new_path)
                    print(f"✅ Đã chuyển & đổi tên: {filename} ➝ {new_filename}")
                except Exception as e:
                    print(f"❌ Lỗi khi di chuyển & đổi tên {filename}: {e}")


# -------------------------------
# **Bước 3: Chia video vào 4 thư mục tương ứng**
# -------------------------------
def organize_videos_by_action(root_folder):
    """Duyệt tất cả video trong 'all_videos/' và chia vào 4 thư mục theo động tác"""
    
    # Định nghĩa các động tác
    actions = ["Dangchanraxanghiengminh", "Ngoithangbangtrengot", "Sodatvuonlen", "Xemxaxemgan"]

    # Đường dẫn thư mục chứa tất cả video
    all_videos_folder = os.path.join(root_folder, "all_videos")

    # Tạo 4 thư mục động tác nếu chưa có
    for action in actions:
        action_folder = os.path.join(root_folder, action)
        if not os.path.exists(action_folder):
            os.makedirs(action_folder)

    # Duyệt tất cả video trong all_videos/
    for filename in os.listdir(all_videos_folder):
        file_path = os.path.join(all_videos_folder, filename)

        # Bỏ qua nếu không phải file video
        if not filename.endswith(".mp4"):
            continue

        # Xác định động tác từ tên file
        for action in actions:
            if action in filename:
                destination_folder = os.path.join(root_folder, action)
                destination_path = os.path.join(destination_folder, filename)

                # Di chuyển file vào thư mục tương ứng
                try:
                    shutil.move(file_path, destination_path)
                    print(f"✅ Đã di chuyển: {filename} ➝ {destination_folder}")
                except Exception as e:
                    print(f"❌ Lỗi khi di chuyển {filename}: {e}")
                break  # Khi tìm thấy động tác, dừng vòng lặp để tránh xét thêm

    print("🎉 Hoàn tất chia video vào 4 thư mục!")


# -------------------------------
# **Bước 4: Chạy tất cả trong main()**
# -------------------------------
def main():
    # Dictionary mapping ID với tên thí sinh (định dạng chuẩn)
    members_dict = {
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

    # Mapping ID thiết bị
    device_dict = {
        "iPhone": "01",
        "Samsung": "02",
        "Oppo": "03"
    }

    # Thư mục gốc chứa tất cả video
    root_folder = r"D:\FPT\CN9\Thesis\private_data"  # 🛠 Thay đường dẫn phù hợp
    output_folder = os.path.join(root_folder, "all_videos")  # Thư mục đích

    # Gọi hàm đổi tên file video
    rename_videos(root_folder, members_dict, device_dict, output_folder)
    organize_videos_by_action(root_folder)


    print("🎉 Hoàn tất quá trình xử lý video!")

if __name__ == "__main__":
    main()
