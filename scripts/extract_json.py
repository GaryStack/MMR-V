import json
import random
import os
import sys
import re
import json
sys.path.append(os.path.abspath("/netdisk/zhukejian/implicit_video_anonotations"))
# print(sys.path)
import time
# 最大重试次数
MAX_RETRIES = 3
import argparse
from utils.video_utils import OpenAI, VIDEO_TOKEN
from utils import write_to_json

# LLM 调用配置
# api_key = "your_api_key"
model_name = "gpt-4o"

client = OpenAI(
    model_version=model_name,
    api_type='openai',
    api_key=api_key,
    api_url="https://api.gpt.ge/v1/chat/completions",
    default_headers={"x-foo": "true"},
)

# 调用 LLM 解析 `gpt-4o_response`
def extract_options_with_llm(text):
    full_prompt = f"""Extract the multiple-choice options from the given text and return them in a JSON array. Only extract options and do not modify their content.

    Input:
    {text}

    Output (JSON format):
    {{
        "options": [
            "(A) First option text.",
            "(B) Second option text.",
            "(C) Third option text.",
            "(D) Fourth option text."
        ]
    }}
    """

    response = client.generate(contexts=full_prompt)
    # breakpoint()
    try:
        pattern = r'"options"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, response, re.DOTALL)
        # breakpoint()
        if match:
            options_text = match.group(1)  # 提取 options 数组内容
            options_list = re.findall(r'"(.*?)"', options_text)  # 提取所有的字符串选项
            return options_list
        # extracted_data = json.loads(match)  # 确保返回的是 JSON
        else :
            return None
    except json.JSONDecodeError:
        print("API 返回的 JSON 解析失败，返回空列表")
        return []

def clean_option(option):
    """如果选项前面有 (A), (B), ... 这样的编号，就去掉"""
    return re.sub(r"^\([A-Z]\)\s*", "", option)

# 处理 JSON 数据
def process_json(data):
    video = data["video"]
    videoType = data["videoType"]
    question = data["question"]
    reference_answer = data["reference answer"]

    gpt_response = data.get("gpt-4o_response", "")  # 获取 gpt-4o_response，避免 KeyError
    options = []

    # 确保 gpt-4o_response 是字符串
    if isinstance(gpt_response, dict):
        print(f"警告：gpt-4o_response 不是字符串，而是字典，数据 -> {gpt_response}")
        gpt_response = json.dumps(gpt_response)  # 如果是字典，先转换成字符串

    if gpt_response.strip():  # 确保不为空
        try:
            parsed_response = json.loads(gpt_response)  # 尝试解析 JSON
            if "options" in parsed_response:
                options = parsed_response["options"]
            else:
                print(f"警告：gpt-4o_response 解析后缺少 'options' 字段 -> {parsed_response}")
        except json.JSONDecodeError:
            print(f"警告：gpt-4o_response 不是有效 JSON，尝试用 LLM 解析 -> {gpt_response}")
            options = extract_options_with_llm(gpt_response)  # 走 LLM 解析
    else:
        print(f"警告：gpt-4o_response 为空，跳过解析 -> {data}")
    # breakpoint()
    # 确保 options 不是空的
    if not options:
        print(f"错误：未能提取选项，跳过该条数据 -> {question}")
        return None

    # # 随机插入 reference_answer
    # insert_index = random.randint(0, len(options))
    # options.insert(insert_index, reference_answer)
    # correct_answer_label = f"({chr(65 + insert_index)})"

    # # 重新编号选项
    # options = [f"({chr(65 + i)}) {opt}" for i, opt in enumerate(options)]
    options = [clean_option(opt) for opt in options]

    # 先去掉 reference_answer 里可能的 (X) 标号
    reference_answer = clean_option(reference_answer)

    # 随机选择插入 reference_answer 的位置
    insert_index = random.randint(0, len(options))

    # 插入 reference answer
    options.insert(insert_index, reference_answer)

    # 重新编号选项
    options = [f"({chr(65 + i)}) {opt}" for i, opt in enumerate(options)]

    # 计算正确答案的标号
    correct_answer_label = f"({chr(65 + insert_index)})"

    return {
        "video": video,
        "videoType": videoType,
        "remark": "",
        "question": question,
        "options": options,
        "correctAnswer": correct_answer_label,
        "abilityType_L2": "",
        "abilityType_L3": ""
    }

# 读取本地 JSON 文件，处理每条数据并保存
def process_json_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        data_list = json.load(f)  # 读取整个 JSON 文件为列表

    processed_data_list = []
    for data in data_list:
        processed_entry = process_json(data)
        if processed_entry:  # 确保数据有效才添加
            processed_data_list.append(processed_entry)
        else :
            processed_data_list.append(data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed_data_list, f, indent=4, ensure_ascii=False)  # 保存处理后的数据

if __name__ == '__main__':
    print("Generating Questions and Answers")
    parser = argparse.ArgumentParser()
    parser.add_argument('--annotation_date', type=str)
    args = parser.parse_args()
    # 指定输入和输出文件
    input_file = f'/netdisk/zhukejian/implicit_video_anonotations/annotation/{args.annotation_date}_IV_Bench.json'  # 本地输入 JSON 文件
    output_file = f"/netdisk/zhukejian/implicit_video_anonotations/annotation/{args.annotation_date}_IV_Bench_output.json"  # 处理后的 JSON 文件

    process_json_file(input_file, output_file)
    print(f"数据处理完成，已保存至 {output_file}")
