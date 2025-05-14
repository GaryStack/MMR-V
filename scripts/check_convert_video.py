import os
import subprocess
from decord import VideoReader, cpu
from concurrent.futures import ThreadPoolExecutor

def check_video_readable(video_path):
    """检查视频文件是否可以被 decord.VideoReader 读取"""
    try:
        vr = VideoReader(video_path, ctx=cpu(0), num_threads=1)
        return True
    except Exception as e:
        if "ERROR cannot find video stream" in str(e):
            return False
        return True  # 其他错误暂不处理

def convert_video(video_path):
    """如果视频不可读，则进行转码"""
    dir_name, full_filename = os.path.split(video_path)
    file_name, ext = os.path.splitext(full_filename)
    
    # 获取第一个单词作为临时文件名
    temp_name = file_name.split()[0] if " " in file_name else file_name
    temp_path = os.path.join(dir_name, f"{temp_name}{ext}")
    converted_temp_path = os.path.join(dir_name, f"{temp_name}_converted{ext}")

    # 临时重命名，防止 ffmpeg 识别不了空格
    os.rename(video_path, temp_path)

    # 执行 ffmpeg 转码
    ffmpeg_cmd = [
        "ffmpeg", "-i", temp_path, "-c:v", "libx264", "-preset", "fast", 
        "-crf", "23", "-c:a", "aac", "-b:a", "128k", converted_temp_path
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg 转码失败: {video_path}\nError: {e}")
        os.rename(temp_path, video_path)  # 还原文件名
        return

    # 删除原文件，重命名转换后文件为原始文件名
    os.remove(temp_path)
    os.rename(converted_temp_path, video_path)
    print(f"✅ 转码成功: {video_path}")

def process_videos_in_folder(folder_path, max_workers=4):
    """遍历文件夹，检查并处理所有视频"""
    video_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
                   if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm'))]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for video_path in video_files:
            if not check_video_readable(video_path):
                executor.submit(convert_video, video_path)
            else:
                print(f"✅ 可读取: {video_path}")

if __name__ == "__main__":
    folder_path = "/netdisk/zhukejian/implicit_video_anonotations/3_10_downloads"  # 替换成你的文件夹路径
    process_videos_in_folder(folder_path)
