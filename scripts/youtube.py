import subprocess
import sys
import os

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
def download_youtube_video(url, output_folder="./3_4_downloads", proxy=None, cookies_file=None):
    # 确保输出目录存在
    os.makedirs(output_folder, exist_ok=True)

    # yt-dlp 命令构建
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",  # 选择最佳视频+音频格式
        "--merge-output-format", "mp4",  # 合并格式为 mp4
        "-o", f"{output_folder}/%(title)s.%(ext)s",  # 输出文件路径
        url
    ]

    # 代理支持（如果提供）
    if proxy:
        cmd += ["--proxy", proxy]

    # 使用 cookies 认证（如果提供）
    if cookies_file:
        cmd += ["--cookies", cookies_file]

    # 运行 yt-dlp
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 下载完成: {url}")
    except subprocess.CalledProcessError:
        print(f"❌ 下载失败: {url}")

if __name__ == "__main__":
    # install_or_update_yt_dlp()  # 确保 yt-dlp 最新
    # check_ffmpeg()  # 确保 ffmpeg 可用

    # 用户输入 YouTube 视频 URL
    video_url = input("请输入 YouTube 视频链接: ").strip()

    # 下载视频
    download_youtube_video(video_url)

    print("🎉 下载任务完成！")
