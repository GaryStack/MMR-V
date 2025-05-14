import os
import subprocess

def download_video(url, output_folder):
    """
    下载视频并保存为 MP4 格式。

    :param url: 视频的 URL（支持 YouTube、Bilibili 等）。
    :param output_folder: 保存视频的目标文件夹。
    """
    # 确保目标文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 设置输出文件模板
    output_template = os.path.join(output_folder, "%(title)s.%(ext)s")

    # 下载命令
    command = [
        "yt-dlp",  # 替代 youtube-dl 使用 yt-dlp
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",  # 下载最佳质量的 MP4 视频
        "--merge-output-format", "mp4",  # 合并音视频为 MP4 格式
        "-o", output_template,  # 输出文件路径
        url
    ]

    try:
        # 调用命令行执行下载
        subprocess.run(command, check=True)
        print(f"视频已成功下载到: {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"下载失败: {e}")

if __name__ == "__main__":
    # 示例：下载 YouTube 或 Bilibili 视频
    video_url = "https://www.youtube.com/watch?v=4KvAoF1wcBo"
    save_folder = './static/videos/'

    download_video(video_url, save_folder)
    #  video_page_url = "https://www.bilibili.com/video/BV12T411g7KA/?spm_id_from=888.80997.embed_other.whitelist&t=28.943664&bvid=BV12T411g7KA&vd_source=e2638f46408a99009fc4299e944cf139"
    # "https://www.youtube.com/watch?v=8AsZCKw53lI&list=PL68gfsJwBv3d8k3Bw6B8Qb8bQY0zIFrMW&index=6"