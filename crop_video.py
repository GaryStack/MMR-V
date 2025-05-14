import os
from moviepy.editor import VideoFileClip

def crop_video(input_video_path, start_time, end_time):
    # 获取文件所在目录和文件名
    dir_name, file_name = os.path.split(input_video_path)
    file_base, file_ext = os.path.splitext(file_name)
    
    # 生成重命名后的原视频路径
    original_video_renamed = os.path.join(dir_name, f"{file_base}123{file_ext}")
    
    # 生成裁剪后的视频路径
    output_video_path = os.path.join(dir_name, f"{file_base}{file_ext}")
    
    # 重命名原视频
    os.rename(input_video_path, original_video_renamed)
    
    # 加载视频文件
    video = VideoFileClip(original_video_renamed)
    
    # 裁剪视频
    cropped_video = video.subclip(start_time, end_time)
    
    # 保存裁剪后的视频
    cropped_video.write_videofile(output_video_path, codec="libx264")
    
    # 删除重命名后的原视频
    os.remove(original_video_renamed)
    
    print(f"原视频已重命名并删除: {original_video_renamed}")
    print(f"裁剪后的视频已保存为: {output_video_path}")

# 使用示例
input_video_path = "/netdisk/zhukejian/implicit_video_anonotations/3_11_downloads/Dinner for few ｜ Animated short film by Nassos Vakalis.mp4"
start_time = 27  # 开始时间（秒）
end_time = 609  # 结束时间（秒）

crop_video(input_video_path, start_time, end_time)
