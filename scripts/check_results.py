import json
import re
import os

def extract_letter_from_brackets(s):
    match = re.search(r'\((\w)\)', s)
    if match:
        return match.group(1)
    else:
        return None

def extract_model_answer(entry, model_name):
    model_response_key = f"{model_name}_response"
    model_raw_response_key = f"{model_name}_raw_response"
    
    # 尝试从结构化响应中获取答案
    if model_response_key in entry:
        response = entry[model_response_key]
        answer = str(response.get('final_answer', '')).strip().upper()
        if answer and answer in 'ABCDEFGHIJKL':
            return answer
        return None
    
    # 尝试从原始响应中提取答案
    raw_response = entry.get(model_raw_response_key, '')
    raw_response_upper = raw_response.upper()
    
    # 正则表达式匹配括号中的字母
    matches = re.findall(r'[\[\(]([A-L])[\]\)]', raw_response_upper)
    if matches:
        return matches[-1]
    
    # 反向查找第一个有效字母
    for char in reversed(raw_response_upper):
        if char in 'ABCDEFGHIJKL':
            return char
    
    return None

def calculate_accuracy(json_path, model_name):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = 0
    correct = 0
    incorrect_entries = []
    
    for entry in data:
        total += 1
        correct_answer = extract_letter_from_brackets(entry['correctAnswer'])
        model_answer = extract_model_answer(entry, model_name)
        # breakpoint()
        if model_answer == correct_answer:
            correct += 1
        else:
            # 添加错误信息到原条目
            entry['false_calc'] = {
                'expected': correct_answer,
                'actual': model_answer,
                'correct': False
            }
            incorrect_entries.append(entry)
        if total>=413:
            break
    print(f"correct: {correct}")
    print(f"total: {total}")
    accuracy = correct / total if total > 0 else 0
    
    # 生成错误文件
    # breakpoint()
    base_name = os.path.splitext(json_path)[0]
    output_path = f"{base_name}_false.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(incorrect_entries, f, indent=4, ensure_ascii=False)
    
    return {
        "total_questions": total,
        "correct_answers": correct,
        "accuracy": accuracy,
        "error_file": output_path
    }

# 使用示例
if __name__ == "__main__":
    # 请替换为实际文件路径和模型名称
    model_name = 'gpt-4o'
    save_dir = f'/netdisk/zhukejian/implicit_video_anonotations/results/{model_name}_on_MMR_V.json'
    result = calculate_accuracy(save_dir, model_name)
    print(f"Accuracy: {result['accuracy']:.2%}")
    print(f"Error file saved to: {result['error_file']}")