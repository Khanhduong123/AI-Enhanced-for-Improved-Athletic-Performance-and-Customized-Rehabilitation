# Đây là file dùng để phân loại video vào thư mục tương ứng, tránh việc làm thủ công nhiều lần.
# Cách hoạt động: truy cập vào folder chứa video và di chuyển vào thư mục theo bài tập.
# Lưu ý: Cần đảm bảo video được lưu đúng thư mục ban đầu.

import os
import shutil

def move_videos(video_folder):
    """
    Di chuyển các file video vào thư mục tương ứng dựa trên tên bài tập.
    Format file: [ID]_[Tên]_[Bài tập].mp4
    Các thư mục đích: Xemxaxemgan, Ngoithangbangtrengot, Dangchanraxanghiengminh, Sodatvuonlen
    """

    # Danh sách thư mục cần tạo
    categories = ["Xemxaxemgan", "Ngoithangbangtrengot", "Dangchanraxanghiengminh", "Sodatvuonlen"]

    # Tạo thư mục nếu chưa có
    for category in categories:
        os.makedirs(os.path.join(video_folder, category), exist_ok=True)

    # Duyệt qua danh sách file trong thư mục
    video_files = [f for f in os.listdir(video_folder) if f.endswith((".mp4", ".avi", ".mov"))]
    print("Video file: ",video_files)
    for file_name in video_files:
        parts = file_name.split("_")
        print('parts', parts)
        if len(parts) >= 3:  # Kiểm tra đúng format
            category = parts[2]  # Lấy phần bài tập từ tên file
            category = category.replace('.mp4', '')
            print(category)
            destination_folder = os.path.join(video_folder, category)

            if category in categories:
                source_path = os.path.join(video_folder, file_name)
                destination_path = os.path.join(destination_folder, file_name)
                
                try:
                    shutil.move(source_path, destination_path)
                    print(f"✅ Đã di chuyển: {file_name} ➝ {destination_folder}")
                except Exception as e:
                    print(f"❌ Lỗi khi di chuyển {file_name}: {e}")

def main():
    # Thư mục chứa video
    video_folder = r"D:\FPT\CN9\Thesis\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\data\raw_video\Oppo"

    if not os.path.exists(video_folder):
        print(f"❌ Lỗi: Thư mục '{video_folder}' không tồn tại.")
        return

    move_videos(video_folder)

if __name__ == "__main__":
    main()
