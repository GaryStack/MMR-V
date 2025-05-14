import json
import re
import os
from collections import defaultdict

REASONING_CATEGORY_MAPPING = {
    # 保持原有映射关系不变
    "Metaphor Understanding": "Implicit",
    "Theme Understanding": "Implicit",
    "Emotion Recognition": "Implicit",
    "Implicit Symbol": "Implicit",
    "Comment Matching": "Implicit",
    "Counterintuitive Reasoning": "Explicit",
    "Causal Reasoning": "Explicit",
    "Sequential Structure Reasoning": "Explicit",
    "Video Type and Intent": "Explicit",
    "Cross-modal Creative Transfer": "Explicit"
}


def extract_letter_from_brackets(s):
    """从括号中提取字母（兼容带空格的情况）"""
    match = re.search(r'\(([A-L])\)', s.strip().upper())
    return match.group(1) if match else None

def extract_model_answer(entry, model_name):
    """提取模型答案（优先结构化响应，次之原始响应）"""
    response_key = f"{model_name}_response"
    raw_key = f"{model_name}_raw_response"
    
    # 优先处理结构化响应
    if response_key in entry:
        final_answer = str(entry[response_key].get('final_answer', '')).strip().upper()
        if final_answer in 'ABCDEFGHIJKL':
            return final_answer
    
    # 处理原始响应
    raw_response = entry.get(raw_key, '').upper()
    
    # 匹配方括号或圆括号中的字母
    bracket_matches = re.findall(r'[\[\(]([A-L])[\]\)]', raw_response)
    if bracket_matches:
        return bracket_matches[-1]
    
    # 逆向搜索第一个有效字母
    for char in reversed(raw_response):
        if char in 'ABCDEFGHIJKL':
            return char
    
    return None

def format_statistics(data_dict):
    """格式化统计结果，包含数量和准确率"""
    formatted = {}
    for category, stats in data_dict.items():
        total = stats['total']
        correct = stats['correct']
        accuracy = f"{correct/total:.2%}" if total > 0 else "N/A"
        formatted[category] = {
            'count': f"{correct}/{total}",
            'accuracy': accuracy
        }
    return formatted

def calculate_accuracy(json_path, model_name):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 初始化统计数据结构（新增video_type统计）
    stats = {
        'total': 0, 'correct': 0,
        'l2': defaultdict(lambda: {'total': 0, 'correct': 0}),
        'l3': defaultdict(lambda: {'total': 0, 'correct': 0}),
        'reasoning': defaultdict(lambda: {'total': 0, 'correct': 0}),
        'video_type': defaultdict(lambda: {'total': 0, 'correct': 0}),
        'errors': []
    }

    for entry in data:
        # 基础信息提取
        correct_letter = extract_letter_from_brackets(entry['correctAnswer'])
        model_letter = extract_model_answer(entry, model_name)
        is_correct = correct_letter == model_letter
        
        # 获取分类信息
        l2_type = entry.get('abilityType_L2', 'Unknown').strip() or 'Unknown'
        l3_type = entry.get('abilityType_L3', 'Unknown').strip() or 'Unknown'
        video_type = entry.get('videoType', 'Unknown').strip() or 'Unknown'  # 新增
        
        # 映射到推理类别
        reasoning_type = REASONING_CATEGORY_MAPPING.get(l2_type, 'Other')

        # 更新统计信息
        stats['total'] += 1
        if is_correct:
            stats['correct'] += 1
            stats['l2'][l2_type]['correct'] += 1
            stats['l3'][l3_type]['correct'] += 1
            stats['reasoning'][reasoning_type]['correct'] += 1
            stats['video_type'][video_type]['correct'] += 1  # 新增
        
        # 更新总数（所有分类都需要更新）
        stats['l2'][l2_type]['total'] += 1
        stats['l3'][l3_type]['total'] += 1
        stats['reasoning'][reasoning_type]['total'] += 1
        stats['video_type'][video_type]['total'] += 1  # 新增

        # 错误记录（保持不变）
        if not is_correct:
            error_entry = entry.copy()
            error_entry['error_info'] = {
                'expected': correct_letter,
                'actual': model_letter,
                'is_correct': False
            }
            stats['errors'].append(error_entry)

    # 生成错误报告文件（保持不变）
    # base_name = os.path.splitext(json_path)[0]
    # error_path = f"{base_name}_errors.json"
    # with open(error_path, 'w', encoding='utf-8') as f:
    #     json.dump(stats['errors'], f, indent=2, ensure_ascii=False)

    return {
        'total': {
            'count': f"{stats['correct']}/{stats['total']}",
            'accuracy': f"{stats['correct']/stats['total']:.2%}" if stats['total'] else "N/A"
        },
        'reasoning': format_statistics(stats['reasoning']),
        'l2': format_statistics(stats['l2']),
        'l3': format_statistics(stats['l3']),
        'video_type': format_statistics(stats['video_type']),  # 新增
        # 'error_report': error_path
    }

if __name__ == "__main__":
    result = calculate_accuracy("/mnt/userdata/implicit_video_anonotations/results/gemini-2.5-flash-preview-04-17_on_MMR_V_new_final.json", "gemini-2.5-flash-preview-04-17")
    # breakpoint()
    print(f"总准确率: {result['total']['count']} ({result['total']['accuracy']})")
    
    print("\n推理类别:")
    for category, data in result['reasoning'].items():
        print(f"  {category}: {data['count']} ({data['accuracy']})")
    
    print("\n视频类型:")
    for category, data in result['video_type'].items():  # 新增输出
        print(f"  {category}: {data['count']} ({data['accuracy']})")
    
    print("\nL2分类:")
    for category, data in result['l2'].items():
        print(f"  {category}: {data['count']} ({data['accuracy']})")
    
    print("\nL3分类:")
    for category, data in result['l3'].items():
        print(f"  {category}: {data['count']} ({data['accuracy']})")
    
    # print(f"\n错误报告已保存至: {result['error_report']}")