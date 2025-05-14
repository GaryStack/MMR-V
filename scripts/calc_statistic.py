import json
import os
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from moviepy.editor import VideoFileClip

# 配置路径
json_file_path = "/netdisk/zhukejian/implicit_video_anonotations/MMR-V.json"
video_folder_path = "/netdisk/zhukejian/implicit_video_anonotations/static/videos"
results_folder = "/netdisk/zhukejian/implicit_video_anonotations/results"
os.makedirs(results_folder, exist_ok=True)

# 读取 JSON 数据
with open(json_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

video_type_count = defaultdict(int)
video_durations = []
video_duration_info = {}

# 新增统计变量
total_question_words = 0
question_count = 0
total_option_words = 0
option_count = 0
ability_type_l2_counter = Counter()
ability_type_l3_counter = Counter()

# 遍历数据
for item in data:
    # 视频类型
    video_type = item["videoType"].capitalize()
    video_type_count[video_type] += 1
    item["videoType"] = video_type

    # 视频路径
    video_filename = item["video"]
    video_path = os.path.join(video_folder_path, video_filename)

    # 视频时长
    if os.path.exists(video_path):
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration  # 秒
            video_durations.append(duration)
            video_duration_info[video_filename] = duration
            clip.close()
        except Exception as e:
            print(f"无法读取视频 {video_filename}: {e}")

    # 问题和选项统计
    for q in item.get("questions", []):
        question_count += 1
        total_question_words += len(q["question"].split())

        for option in q.get("options", []):
            option_count += 1
            total_option_words += len(option.split())

        ability_type_l2_counter[q["abilityType_L2"]] += 1
        ability_type_l3_counter[q["abilityType_L3"]] += 1

# ===== 视频时长统计 =====
if video_durations:
    avg_duration = sum(video_durations) / len(video_durations)
    min_duration = min(video_durations)
    max_duration = max(video_durations)
    shortest_video = min(video_duration_info, key=video_duration_info.get)
    longest_video = max(video_duration_info, key=video_duration_info.get)
else:
    avg_duration = min_duration = max_duration = 0
    shortest_video = longest_video = "N/A"

# 打印视频信息
print("\n====== 视频统计信息 ======")
print(f"视频总数: {len(video_durations)}")
print(f"平均时长: {avg_duration:.2f} 秒")
print(f"最短视频: {shortest_video} ({min_duration:.2f} 秒)")
print(f"最长视频: {longest_video} ({max_duration:.2f} 秒)")

# ===== 问题和选项单词统计 =====
avg_question_words = total_question_words / question_count if question_count else 0
avg_option_words = total_option_words / option_count if option_count else 0
avg_option_count = option_count / question_count if question_count else 0

print("\n====== 语言长度统计 ======")
print(f"问题总数: {question_count}")
print(f"问题平均单词数: {avg_question_words:.2f}")
print(f"选项总数: {option_count}")
print(f"选项平均单词数: {avg_option_words:.2f}")
print(f"平均每题选项数：{avg_option_count:.2f}")

# ===== 能力类型统计 =====
print("\n====== Ability Type L2 ======")
for k, v in ability_type_l2_counter.items():
    print(f"{k}: {v}")

print("\n====== Ability Type L3 ======")
for k, v in ability_type_l3_counter.items():
    print(f"{k}: {v}")

# ===== 绘图：视频时长分布 =====
duration_bins = {
    "0-100s": 0,
    "100-400s": 0,
    "400-1000s": 0,
    "1000-1500s": 0,
    "1500s+": 0
}

for duration in video_durations:
    if duration <= 100:
        duration_bins["0-100s"] += 1
    elif duration <= 400:
        duration_bins["100-400s"] += 1
    elif duration <= 1000:
        duration_bins["400-1000s"] += 1
    elif duration <= 1500:
        duration_bins["1000-1500s"] += 1
    else:
        duration_bins["1500s+"] += 1

# 绘图
plt.figure(figsize=(8, 5))
plt.bar(duration_bins.keys(), duration_bins.values(), color='skyblue')
plt.xlabel("视频时长范围（秒）")
plt.ylabel("视频数量")
plt.title("视频时长分布")
plt.xticks(rotation=30)
plt.grid(axis="y", linestyle="--", alpha=0.7)

pdf_path = os.path.join(results_folder, "video_duration_distribution.pdf")
plt.savefig(pdf_path, format="pdf", bbox_inches="tight")
plt.close()

print(f"\n视频时长分布图已保存至: {pdf_path}")
