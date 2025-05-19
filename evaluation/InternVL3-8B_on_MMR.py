from dotenv import load_dotenv 
import sys
import os
import json
import argparse
import re
# 加载 .env 文件中的环境变量
# load_dotenv()
# 从环境变量中获取 API 密钥
from loguru import logger as eval_logger
from utils.video_utils import OpenAI,VIDEO_TOKEN
from utils import write_to_json, read_json
from dataset.load_MMR_V import load_MMR_V

prompt_template = """
[[INSTRUCTIONS]]
Please select the best answer to the following multiple-choice question based on the video. 
Only one option is the most accurate answer in relation to the question and the video.

What is the correct answer to this question [[QUESTION]]
Options:
[[OPTIONS]]
[[END OF INSTRUCTIONS]]
[[QUESTION]]
{question}
[[END OF QUESTION]]
[[OPTIONS]]
{options}
[[END OF OPTIONS]]
[[OUTPUT FORMAT]]
Format your answer as follows:
If the correct option letters (A, B, C, D... ) for the multiple-choice question is X,
Directly give the final correct option number in the following format: "[[X]]"
[[END OF OUTPUT FORMAT]]
"""

def extract_last_option(text):
    """从文本中倒序查找最后一个出现的A-D选项"""
    matches = re.findall(r'\b([A-L])\b', text.upper())
    return matches[-1] if matches else None

def get_unique_id(elem):
    return elem["question"]

if __name__ == '__main__':
    print("Hello World")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--api_url",
        type=str,
        default="https://api.gpt.ge/v1/chat/completions",
        help="URL for the API endpoint."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help="API key for authentication."
    )
    parser.add_argument(
        "--continue_eval",
        action="store_true",
        default=True,
        help="continue evaluation from existing result file"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="overwrite the existing result file"
    )
    args = parser.parse_args()
    samples = load_MMR_V()
    model_name = 'InternVL3-8B'
    # save_file = f'/netdisk/zhukejian/implicit_video_anonotations/results/{model_name}_on_MMR_V.json'
    # visual_path = '/netdisk/zhukejian/implicit_video_anonotations/static/videos'

    file_paths = [
        # "/mnt/userdata/implicit_video_anonotations/MMR-V - video -llava.json"
        "/netdisk/zhukejian",
        "/mnt/userdata"
    ]

    for path in file_paths:
        if os.path.exists(f"{path}/implicit_video_anonotations"):
            save_file = f'{path}/implicit_video_anonotations/results/{model_name}_on_MMR_V.json'
            visual_path = f'{path}/implicit_video_anonotations/static/videos'            
            break  # 一旦找到有效路径，停止遍历

    results = []
    id_set = set()
    id2sample = {}
    # breakpoint()
    if args.continue_eval:
        if os.path.isfile(save_file):
            print(f"Continue eval from file {save_file}")
            results = read_json(save_file)
            results = [elem for elem in results if elem[f"{model_name}_raw_response"] is not None and elem[f"{model_name}_raw_response"] != ""]
            print(f"Load {len(results)} results...")
            id_set = set([get_unique_id(elem) for elem in results])
            id2sample = {get_unique_id(elem): elem for elem in results}
        else:
            print(f"File {save_file} does not exists! Ignore the continue_eval parameter.")
    elif args.overwrite:
        if os.path.isfile(save_file):
            print(f"Choose to overwrite existing file {save_file}")
        else:
            print(f"File {save_file} does not exists! Ignore the overwrite parameter.")
    else:
        if os.path.isfile(save_file):
            raise ValueError(f"Save file {save_file} already exists! Please use --continue_eval or  --overwrite.")

    client = OpenAI(
        model_version=model_name,
        api_type='openai',
        api_key="",
        api_url="http://210.75.240.156:52578/v1/chat/completions",
        default_headers={"x-foo": "true"},
        max_num_frames=8,
    )
    # breakpoint()
    
    for idx,sample in enumerate(samples[:]):
        
        curr_id = get_unique_id(sample)
        if curr_id in id_set and id2sample[curr_id][f"{model_name}_raw_response"] is not None and id2sample[curr_id][f"{model_name}_raw_response"] != "":
            continue
        
        print(f"******** idx={idx} **********")
        
        video_path = os.path.join(visual_path,sample["video"])
        question = sample["question"]
        options = sample["options"]
        full_prompt = prompt_template.format(
            question=question,
            options=options,
        )

        response = client.generate(
            visuals=video_path,
            contexts=f'{full_prompt} {VIDEO_TOKEN}'
        )
        print(response)
        sample[f"{model_name}_raw_response"] = response

        if isinstance(response, str):
            # 先尝试原始的 [[X]] 提取
            json_regex = r'\[\[([A-L])\]\]'
            match = re.search(json_regex, response)
            if match:
                final_answer = match.group(1)
                sample[f"{model_name}_response"] = {"final_answer": final_answer}
                print(f"Extracted answer: {final_answer}")
            else:
                # 回退到 \boxed{X} 格式的提取
                box_regex = r'\\boxed\{([A-L])\}'
                box_match = re.search(box_regex, response)
                if box_match:
                    final_answer = box_match.group(1)
                    sample[f"{model_name}_response"] = {"final_answer": final_answer}
                    print(f"Extracted answer from boxed pattern: {final_answer}")
                else:
                    option = extract_last_option(response)
                    if option:
                        sample[f"{model_name}_response"] = {"final_answer": option}
                    else:
                        print("No matching answer found in response.")
                        # 仍然存储原始响应以便检查
                        sample[f"{model_name}_raw_response"] = response
        else:
            print("Invalid response type received.")
            sample[f"{model_name}_raw_response"] = "Error: Invalid response type"

        results.append(sample)
        # Write the results to the output file
        write_to_json(results, save_file, indent=4)

    eval_logger.info(f"Successfully wrote {len(results)} results to {save_file}!")
    eval_logger.info("Finished Running!")
