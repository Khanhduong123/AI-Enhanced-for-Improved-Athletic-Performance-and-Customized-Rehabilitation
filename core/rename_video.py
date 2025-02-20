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
    video_folder = "D:\FPT\CN9\Thesis\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\data\dummysquat" # không biết đổi làm sao để rút ngắn lại

    # Dictionary cung cấp thông tin đổi tên
    rename_dict = {
        1: ["001", "NguyenVanA", "DangChanRaXaNghiengMinh"],
        2: ["002", "TranVanB", "DangChanRaXaNghiengMinh"],
        3: ["003", "LeThiC", "DangChanRaXaNghiengMinh"]
    }

    if not os.path.exists(video_folder):
        print(f"❌ Lỗi: Thư mục '{video_folder}' không tồn tại.")
        return

    rename_videos(video_folder, rename_dict)

if __name__ == "__main__":
    main()