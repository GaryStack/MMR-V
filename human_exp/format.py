import json
import random

# 配置路径和键名
file_path = "/netdisk/zhukejian/implicit_video_anonotations/human_exp/questions.json"
keys_to_remove = ['error_info', 'gpt-4o_raw_response', 'gpt-4o_response', 'correctAnswer']  # 需要删除的键（按需修改）
keys_to_add = ['human_answer', 'cost_time', 'explanation']      # 需要新增的键（按需修改）

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"读取文件失败: {e}")
    exit()

# 改进后的删除逻辑：先检查存在性
for sample in data:
    for key in keys_to_remove:
        if key in sample:  # 显式存在性检查
            sample.pop(key)
            print(f"已删除存在的键: {key}")
        else:
            print(f"键不存在，跳过删除: {key}")
# breakpoint()
# 添加新键（空字符串值）
for sample in data:
    for key in keys_to_add:
        if key not in sample:  # 可选：防止覆盖已有键
            sample[key] = ""
            print(f"已添加新键: {key}")
        else:
            print(f"键已存在，跳过添加: {key}")

random.shuffle(data)

# 写回文件
output_file_path = "/netdisk/zhukejian/implicit_video_anonotations/human_exp/human_exp_questions.json"
try:
    with open(output_file_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("文件更新成功！")
except Exception as e:
    print(f"写入文件失败: {e}")