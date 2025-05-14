from flask import Flask, send_from_directory, render_template, request, jsonify
import json
import os
import requests
import subprocess


app = Flask(__name__, static_folder='./static')
VIDEO_FOLDER = './static/videos' #
ANNOTATION_FILE = './annotation.json'

@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(app.static_folder + '/videos', filename, mimetype='video/mp4')



def load_annotations():
    """加载现有的标注数据"""
    if os.path.exists(ANNOTATION_FILE):
        try:
            with open(ANNOTATION_FILE, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:  # 文件为空
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading annotations: {e}")
            return []
    return []


def save_annotations(data):
    """保存标注数据到文件"""
    try:
        with open(ANNOTATION_FILE, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving annotations: {e}")


@app.route('/')
def index():
    all_files = os.listdir(VIDEO_FOLDER)
    # 只保留 .mp4 文件
    mp4_files = [f for f in all_files if f.endswith('.mp4')]
    annotations = load_annotations()  # 加载现有的标注数据
    return render_template('index.html', videos=mp4_files, annotations=annotations)

# @app.route('/')
# def index():
#     # 获取视频目录下的所有文件
#     all_files = os.listdir(VIDEO_FOLDER)
#     # 只保留 .mp4 文件
#     mp4_files = [f for f in all_files if f.endswith('.mp4')]
#     # 将文件列表传递给模板
#     return render_template('index.html', videos=mp4_files)


@app.route('/save', methods=['POST'])
def save():
    try:
        # 获取前端提交的数据
        data = request.get_json()
        video = data.get('video')
        remark = data.get('remark', '')
        video_type = data.get('videoType', 'other')
        questions = data.get('questions', [])

        # 数据验证
        if not video:
            return jsonify({'message': '视频名称不能为空！'}), 400

        if not isinstance(questions, list):
            return jsonify({'message': '问题列表格式不正确！'}), 400

        # 加载现有的标注数据
        annotations = load_annotations()

        # 更新或添加新的标注数据
        updated = False
        for entry in annotations:
            if entry['video'] == video:
                entry['remark'] = remark
                entry['videoType'] = video_type
                entry['questions'] = questions
                updated = True
                break

        if not updated:
            annotations.append({
                'video': video,
                'remark': remark,
                'videoType': video_type,
                'questions': questions
            })

        # 保存数据到文件
        save_annotations(annotations)
        return jsonify({'message': '标注已成功保存！'}), 200

    except Exception as e:
        print(f"Error saving annotation: {e}")
        return jsonify({'message': f'保存失败: {str(e)}'}), 500


def download_video(url, output_folder):
    """
    下载视频并保存为 MP4 格式。
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_template = os.path.join(output_folder, "%(title)s.%(ext)s")
    command = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "--merge-output-format", "mp4",
        "-o", output_template,
        url
    ]

    try:
        subprocess.run(command, check=True)
        return True, "视频已成功下载。"
    except subprocess.CalledProcessError as e:
        return False, f"W下载失败: {e}"

@app.route('/download_video', methods=['POST'])
def download_video_route():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"message": "请提供视频链接。"}), 400

    success, message = download_video(video_url, VIDEO_FOLDER)

    if success:
        return jsonify({"message": "视频下载成功！"})
    else:
        return jsonify({"message": message}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=18888)
