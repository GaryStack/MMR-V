import ffmpeg

def crop_video(input_path, output_path):
    # 获取视频信息
    probe = ffmpeg.probe(input_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream is None:
        raise ValueError("No video stream found in input file")
    
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    
    # 计算裁剪的高度
    new_height = int(height * 0.6)  # 90% - 10% = 80%
    y_offset = int(height * 0.2)    # 从10%处开始
    
    # 使用 ffmpeg 进行裁剪
    ffmpeg.input(input_path).crop(x=0, y=y_offset, width=width, height=new_height).output(output_path).run()
    
    print(f"裁剪完成，输出文件: {output_path}")

# 示例调用
input_video = ""
output_video = ""
crop_video(input_video, output_video)