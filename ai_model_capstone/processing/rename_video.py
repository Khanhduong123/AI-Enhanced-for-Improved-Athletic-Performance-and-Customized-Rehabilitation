# đây là file dùng để đổi tên video trong thư mục lưu trữ, tránh phải lặp đi lặp lại việc đổi tên 12x4 lần
# cách hoạt động: truy cập vào folder chứa video và đổi tên ngay tại folder đó --> cần cẩn trọng trong việc lưu video vào folder
import os

def rename_videos(video_folder, rename_dict):
    """
    Đổi tên các file video trong thư mục theo format: [ID]_[Tên]_[Bài tập].mp4
    """
    # Lấy danh sách file video trong thư mục
    video_files = [f for f in os.listdir(video_folder) if f.endswith((".mp4", ".avi", ".mov"))]
    
    # Sắp xếp danh sách file theo thứ tự index của dictionary
    video_files.sort()  # Đảm bảo thứ tự video đúng
    
    if len(video_files) != len(rename_dict):
        print("❌ Lỗi: Số lượng video không khớp với dictionary.")
        return
    
    for idx, (key, value) in enumerate(rename_dict.items()):
        old_file = os.path.join(video_folder, video_files[idx])  # File gốc
        new_file_name = f"{value[0]}_{value[1]}_{value[2]}.mp4"  # Định dạng tên mới
        new_file = os.path.join(video_folder, new_file_name)

        try:
            os.rename(old_file, new_file)
            print(f"✅ Đã đổi tên: {video_files[idx]} ➝ {new_file_name}")
        except Exception as e:
            print(f"❌ Lỗi khi đổi tên {video_files[idx]}: {e}")

def main():
    # Thư mục chứa video
    video_folder = r"D:\FPT\CN9\Thesis\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\data\raw_video\Oppo" # không biết đổi làm sao để rút ngắn lại

    # Dictionary cung cấp thông tin đổi tên
    rename_dict = {
        1: ["1", "LePhanTheVinh", "Xemxaxemgan"],
        2: ["1", "LePhanTheVinh", "Ngoithangbangtrengot"],
        3: ["1", "LePhanTheVinh", "Dangchanraxanghiengminh"],
        4: ["1", "LePhanTheVinh", "Sodatvuonlen"],
        5: ["2", "NguyenCatTuong", "Xemxaxemgan"],
        6: ["2", "NguyenCatTuong", "Ngoithangbangtrengot"],
        7: ["2", "NguyenCatTuong", "Dangchanraxanghiengminh"],
        8: ["2", "NguyenCatTuong", "Sodatvuonlen"],
        9: ["3", "VuDucThienDung", "Xemxaxemgan"],
        10: ["3", "VuDucThienDung", "Ngoithangbangtrengot"],
        11: ["3", "VuDucThienDung", "Dangchanraxanghiengminh"],
        12: ["3", "VuDucThienDung", "Sodatvuonlen"],
        13: ["4", "NguyenNgocNhuThao", "Xemxaxemgan"],
        14: ["4", "NguyenNgocNhuThao", "Ngoithangbangtrengot"],
        15: ["4", "NguyenNgocNhuThao", "Dangchanraxanghiengminh"],
        16: ["4", "NguyenNgocNhuThao", "Sodatvuonlen"],
        17: ["5", "HoangVanLong", "Xemxaxemgan"],
        18: ["5", "HoangVanLong", "Ngoithangbangtrengot"],
        19: ["5", "HoangVanLong", "Dangchanraxanghiengminh"],
        20: ["5", "HoangVanLong", "Sodatvuonlen"],
        21: ["6", "VoLeThanhTuyen", "Xemxaxemgan"],
        22: ["6", "VoLeThanhTuyen", "Ngoithangbangtrengot"],
        23: ["6", "VoLeThanhTuyen", "Dangchanraxanghiengminh"],
        24: ["6", "VoLeThanhTuyen", "Sodatvuonlen"],
        25: ["7", "LuongHoangTrucVan", "Xemxaxemgan"],
        26: ["7", "LuongHoangTrucVan", "Ngoithangbangtrengot"],
        27: ["7", "LuongHoangTrucVan", "Dangchanraxanghiengminh"],
        28: ["7", "LuongHoangTrucVan", "Sodatvuonlen"],
        29: ["8", "DoanVanNghia", "Xemxaxemgan"],
        30: ["8", "DoanVanNghia", "Ngoithangbangtrengot"],
        31: ["8", "DoanVanNghia", "Dangchanraxanghiengminh"],
        32: ["8", "DoanVanNghia", "Sodatvuonlen"],
    }

    if not os.path.exists(video_folder):
        print(f"❌ Lỗi: Thư mục '{video_folder}' không tồn tại.")
        return

    rename_videos(video_folder, rename_dict)

if __name__ == "__main__":
    main()