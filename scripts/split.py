import json

def split_questions(input_json):
    split_data = []
    
    for item in input_json:
        video = item["video"]
        video_type = item["videoType"]
        
        for question_item in item["questions"]:
            split_entry = {
                "video": video,
                "videoType": video_type,
                "remark": "",
                "question": question_item["question"],
                "options": question_item["options"],
                "correctAnswer": question_item["correctAnswer"],
                "abilityType_L2": question_item["abilityType_L2"],
                "abilityType_L3": question_item["abilityType_L3"]
            }
            
            split_data.append(split_entry)
    
    return split_data

# 读取输入 JSON
input_file = "/netdisk/zhukejian/implicit_video_anonotations/MMR-V.json"  # 替换为你的输入文件路径
output_file = "/netdisk/zhukejian/implicit_video_anonotations/MMR-V - split.json"

with open(input_file, "r", encoding="utf-8") as f:
    input_data = json.load(f)

# 拆分数据
output_data = split_questions(input_data)

# 保存输出 JSON
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print("拆分完成，结果保存在", output_file)
