import os
import json
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
    
    temp_name = file_name.split()[0] if " " in file_name else file_name
    temp_path = os.path.join(dir_name, f"{temp_name}{ext}")
    converted_temp_path = os.path.join(dir_name, f"{temp_name}_converted{ext}")

    os.rename(video_path, temp_path)

    ffmpeg_cmd = [
        "ffmpeg", "-i", temp_path, "-c:v", "libx264", "-preset", "fast", 
        "-crf", "23", "-c:a", "aac", "-b:a", "128k", converted_temp_path
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg 转码失败: {video_path}\nError: {e}")
        os.rename(temp_path, video_path)
        return

    os.remove(temp_path)
    os.rename(converted_temp_path, video_path)
    print(f"✅ 转码成功: {video_path}")

def process_videos_from_json(json_path, video_folder, max_workers=4):
    """从 JSON 文件中读取视频列表，检查并处理文件"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    video_files = [os.path.join(video_folder, item["video"]) for item in data if "video" in item]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for video_path in video_files:
            if os.path.exists(video_path):
                if not check_video_readable(video_path):
                    executor.submit(convert_video, video_path)
                else:
                    print(f"✅ 可读取: {video_path}")
            else:
                print(f"❌ 文件不存在: {video_path}")

if __name__ == "__main__":
    json_path = "/netdisk/zhukejian/implicit_video_anonotations/video reasoning split.json"  # 替换为你的 JSON 文件路径
    video_folder = "/netdisk/zhukejian/implicit_video_anonotations/static/videos"  # 替换为你的视频存放目录
    process_videos_from_json(json_path, video_folder)
