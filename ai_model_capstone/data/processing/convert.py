import os

def convert_mov_files(directory):
    """Đổi đuôi .MOV thành .MP4 trong thư mục"""
    for filename in os.listdir(directory):
        if filename.lower().endswith(".mov"):
            old_path = os.path.join(directory, filename)
            new_path = os.path.splitext(old_path)[0] + ".mp4"
            try:
                os.rename(old_path, new_path)
                print(f"✅ Đã đổi tên: {filename} ➝ {os.path.basename(new_path)}")
            except Exception as e:
                print(f"❌ Lỗi khi đổi tên {filename}: {e}")