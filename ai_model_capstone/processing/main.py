import convert
import rename
import classify
import format

def main():
    print("🔥 Bắt đầu xử lý video...")
    
    # # 1️⃣ Chuyển đổi file .MOV → .MP4
    # convert.convert_mov_files("data/raw_video")
    
    # # 2️⃣ Đổi tên file theo format chuẩn
    # rename.rename_videos(r"D:\FPT\CN9\Thesis\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\data\private_data")
    
    # # 3️⃣ Format lại tên file và sắp xếp thư mục
    # format.format_videos(r"D:\FPT\CN9\Thesis\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\data\private_data")

    # # 4️⃣ Phân loại video vào thư mục động tác
    # classify.move_videos(r"D:\FPT\CN9\Thesis\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\ai_model_capstone\data\private_data\all_videos")
    
    print("✅ Hoàn tất xử lý video!")

if __name__ == "__main__":
    main()
