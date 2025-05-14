import json
from collections import defaultdict

def merge_json(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    merged_data = defaultdict(lambda: {"video": "", "videoType": "", "remark": "", "questions": []})
    
    for item in data:
        video = item["video"]
        if not merged_data[video]["video"]:
            merged_data[video]["video"] = video
            merged_data[video]["videoType"] = item["videoType"]
            merged_data[video]["remark"] = ""
        
        question_entry = {
            "question": item["question"],
            "options": item["options"],
            "correctAnswer": item["correctAnswer"],
            "abilityType_L2": item["abilityType_L2"],
            "abilityType_L3": item["abilityType_L3"]
        }
        merged_data[video]["questions"].append(question_entry)
    
    result = list(merged_data.values())
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    print(f"Merged data saved to {output_file}")

# 调用函数，替换 'input.json' 和 'output.json' 为你的实际文件路径
merge_json('/netdisk/zhukejian/implicit_video_anonotations/video reasoning split.json', '/netdisk/zhukejian/implicit_video_anonotations/video reasoning.json')
