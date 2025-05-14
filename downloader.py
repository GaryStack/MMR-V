import subprocess
import sys
import os
import json

# 确保 yt-dlp 已安装或更新
def install_or_update_yt_dlp():
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], check=True)
        print("✅ yt-dlp 已安装/更新成功！")
    except subprocess.CalledProcessError:
        print("❌ 安装/更新 yt-dlp 失败，请手动安装！")
        sys.exit(1)

# 检查 ffmpeg 是否安装
def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("✅ ffmpeg 已安装")
    except FileNotFoundError:
        print("❌ 未找到 ffmpeg，请先安装！")
        sys.exit(1)

# 下载 YouTube 视频
def download_youtube_video(url, output_folder="./3_13_downloads", cookies_file="cookies.txt"):
    os.makedirs(output_folder, exist_ok=True)
    
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",  
        "--merge-output-format", "mp4",  
        "-o", f"{output_folder}/%(title)s.%(ext)s",  
        url
    ]
    
    # 使用 Cookies 认证
    if cookies_file and os.path.exists(cookies_file):
        cmd += ["--cookies", cookies_file]

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 下载完成: {url}")
    except subprocess.CalledProcessError:
        print(f"❌ 下载失败: {url}")

if __name__ == "__main__":
    # install_or_update_yt_dlp()
    # check_ffmpeg()
    
    json_file = "videos.json"
    
    if not os.path.exists(json_file):
        print(f"❌ 未找到 JSON 文件: {json_file}")
        sys.exit(1)
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    video_urls = data.get("videos", [])
    
    if not video_urls:
        print("❌ JSON 文件中未找到有效的 YouTube 视频 URL！")
        sys.exit(1)
    
    for url in video_urls:
        download_youtube_video(url)
    
    print("🎉 所有视频下载任务完成！")
