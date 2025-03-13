import streamlit as st
import requests
import tempfile
import os
import time
from io import BytesIO
import subprocess
import atexit

# =========================
# CẤU HÌNH API ENDPOINTS
# =========================
BASE_URL = "http://localhost:7860/api/v1"
PREDICT_URL = f"{BASE_URL}/predict/"
SKELETON_URL = f"{BASE_URL}/skeleton/extract"

# =========================
# THIẾT LẬP CHO STREAMLIT
# =========================
st.set_page_config(
    page_title="AI Fitness Coach",
    page_icon="💪",
    layout="wide"
)

# Tạo thư mục tạm nếu chưa tồn tại
temp_dir = r"D:\Thesis_SP25\work\AI-Enhanced-for-Improved-Athletic-Performance-and-Customized-Rehabilitation\backend_capstone\temp_streamlit"
os.makedirs(temp_dir, exist_ok=True)

# Hàm dọn dẹp file tạm khi thoát ứng dụng
def cleanup():
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.error(f"Error deleting {file_path}: {e}")

atexit.register(cleanup)

# =========================
# CSS TÙY CHỈNH
# =========================
st.markdown("""
<style>
/* Màu nền tối cho toàn bộ trang (tuỳ chọn) */
/*
body, .main, .block-container {
    background-color: #1e1e1e !important;
    color: #ffffff !important;
}
*/

/* Ghi đè màu cho st.success, st.error, st.warning... (tất cả .stAlert) */
.stAlert {
    background-color: #2e7d32 !important; /* Xanh lá đậm hơn */
    color: #ffffff !important;           /* Chữ trắng */
    border: none !important;
}

/* Căn giữa các video */
.video-container {
    text-align: center;
    margin: 1rem auto;
}
.video-container video {
    max-width: 100%;
    height: auto;
    border: 2px solid #ccc;
    border-radius: 8px;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =========================
# GIAO DIỆN CHÍNH
# =========================
st.title("AI-Enhanced Athletic Performance Analyzer")
st.markdown("""
### Upload your exercise video for real-time analysis  
*Supports MP4 files up to 50MB*
""")

# Upload video
uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])

if uploaded_file is not None:
    # Lưu file gốc vào thư mục tạm
    temp_input_path = os.path.join(temp_dir, "input_video.mp4")
    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    if st.button("Analyze Performance"):
        try:
            # Tạo 3 cột cho 3 phần
            col_original, col_skeleton, col_analysis = st.columns([2, 2, 3])
            
            with st.spinner("Analyzing movement patterns..."):
                # =========================
                # 1) HIỂN THỊ VIDEO GỐC
                # =========================
                with col_original:
                    st.subheader("Original Video")
                    st.markdown('<div class="video-container">', unsafe_allow_html=True)
                    # Phát video gốc mà không xoay
                    st.video(temp_input_path, start_time=0)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # =========================
                # 2) XỬ LÝ & HIỂN THỊ SKELETON
                # =========================
                with col_skeleton:
                    st.subheader("Skeleton Extraction")
                    with st.spinner("Extracting skeleton..."):
                        skeleton_files = {
                            "video_file": (uploaded_file.name, uploaded_file.getvalue(), "video/mp4")
                        }
                        skeleton_response = requests.post(SKELETON_URL, files=skeleton_files)
                        
                        if skeleton_response.status_code == 200:
                            temp_skeleton_path = os.path.join(temp_dir, "skeleton_video.mp4")
                            with open(temp_skeleton_path, "wb") as f:
                                f.write(skeleton_response.content)
                            
                            # Ép xoay video bằng FFmpeg nếu cần (transpose=1 = xoay 90 độ theo chiều kim đồng hồ)
                            # Nếu video của bạn đã đúng chiều, bạn có thể bỏ phần xoay này.
                            fixed_skeleton_path = os.path.join(temp_dir, "fixed_skeleton_video.mp4")
                            try:
                                subprocess.run([
                                    'ffmpeg', '-i', temp_skeleton_path,
                                    '-vf', 'transpose=1',
                                    '-metadata:s:v:0', 'rotate=0',
                                    '-vcodec', 'libx264', '-acodec', 'aac',
                                    '-movflags', 'faststart',
                                    '-pix_fmt', 'yuv420p',
                                    '-y', fixed_skeleton_path
                                ], check=True)
                                
                                # Hiển thị video skeleton đã xoay
                                st.markdown('<div class="video-container">', unsafe_allow_html=True)
                                st.video(fixed_skeleton_path)
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            except Exception as conv_error:
                                st.error(f"Could not convert/rotate video: {str(conv_error)}")
                                st.warning("Please download and view the skeleton video locally.")
                                with open(temp_skeleton_path, "rb") as file:
                                    st.download_button(
                                        label="Download Skeleton Video",
                                        data=file,
                                        file_name="skeleton_video.mp4",
                                        mime="video/mp4"
                                    )
                        else:
                            st.error(f"Skeleton extraction failed: {skeleton_response.text}")
                
                # =========================
                # 3) PHÂN TÍCH POSE
                # =========================
                with col_analysis:
                    st.subheader("Pose Analysis")
                    with st.spinner("Classifying pose..."):
                        uploaded_file.seek(0)
                        predict_files = {
                            "video_file": (uploaded_file.name, uploaded_file.getvalue(), "video/mp4")
                        }
                        predict_response = requests.post(PREDICT_URL, files=predict_files)
                        predict_response.raise_for_status()
                        
                        result = predict_response.json()
                        
                        # Hiển thị kết quả
                        st.success("Analysis complete!")
                        st.markdown(f"**Detected Pose:** {result['prediction']}")
                        
                        # Mô tả chi tiết cho từng pose
                        pose_descriptions = {
                            "Garland_Pose": "A deep squat pose that stretches the ankles, groins and back torso.",
                            "Happy_Baby_Pose": "A pose that gently stretches the inner groins and back.",
                            "Head_To_Knee_Pose": "A forward bend that stretches the hamstrings and spine.",
                            "Lunge_Pose": "Stretches the thighs and groins and opens the chest.",
                            "Mountain_Pose": "The foundation of all standing poses, improves posture.",
                            "Plank_Pose": "Strengthens the arms, wrists, and spine.",
                            "Raised_Arms_Pose": "Stretches the entire body and improves breathing.",
                            "Seated_Forward_Bend": "Calms the brain and stretches the spine and hamstrings.",
                            "Staff_Pose": "Improves posture and strengthens the back muscles.",
                            "Standing_Forward_Bend": "Stretches the hamstrings and calms the nervous system."
                        }
                        
                        detected_pose = result['prediction']
                        if detected_pose in pose_descriptions:
                            st.markdown(f"**Description:** {pose_descriptions[detected_pose]}")
            
            # =========================
            # PHÂN TÍCH CHI TIẾT (EXPANDER)
            # =========================
            with st.expander("View Technical Breakdown"):
                st.write("Joint Angle Metrics:", result.get('joint_angles', "Not available"))
                st.write("Form Suggestions:", result.get('form_suggestions', [
                    "Maintain proper alignment",
                    "Keep breathing steady"
                ]))
            
            # =========================
            # TÀI LIỆU API (EXPANDER)
            # =========================
            with st.expander("API Documentation"):
                st.markdown("""
                **Backend API Endpoints**  
                - POST `/v1/predict` - Classifies the yoga pose in the video  
                - POST `/v1/skeleton/extract` - Extracts and visualizes the skeleton  
                """)
        
        except requests.exceptions.ConnectionError:
            st.error("Backend service unavailable. Please ensure the FastAPI server is running.")
        except requests.exceptions.HTTPError as e:
            st.error(f"Analysis failed: {e.response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

st.markdown("---")
st.caption("Developed using MediaPipe pose estimation and custom deep learning models")
