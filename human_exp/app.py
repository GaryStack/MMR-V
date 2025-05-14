from flask import Flask, render_template, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

# 首页：题目列表页
@app.route('/')
def index():
    return render_template("index.html")

# 单独题目作答页
@app.route('/question')
def question():
    return render_template("question.html")

# 交卷结果页面
@app.route('/result')
def result():
    return render_template("result.html")

# 提供 JSON 数据接口
@app.route('/questions.json')
def get_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
        return jsonify(questions)
    except Exception as e:
        return jsonify({"error": "无法加载题目数据", "details": str(e)}), 500

# 提供视频文件访问（假设视频存放在 /netdisk/implicit/videos/）
@app.route('/netdisk/zhukejian/implicit_video_anonotations/static/videos/<path:filename>')
def serve_video(filename):
    # 注意：根据实际环境，确保 Flask 有权访问该目录。
    video_directory = "/netdisk/zhukejian/implicit_video_anonotations/static/videos"
    if os.path.exists(os.path.join(video_directory, filename)):
        return send_from_directory(video_directory, filename)
    else:
        return f"视频文件 {filename} 不存在！", 404

if __name__ == "__main__":
    # 开发环境中启动 Flask 服务器
    app.run(debug=True)
