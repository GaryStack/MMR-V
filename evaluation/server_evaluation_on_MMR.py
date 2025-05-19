from dotenv import load_dotenv 
import sys
import os
from datasets import load_dataset
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

cot_prompt_template = """
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
Your thinking process.
If the correct option letters (A, B, C, D... ) for the multiple-choice question is X,
give the final correct option number in the following format: "[[X]]"
The final correct option letter MUST be put in the "[[]]"
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
        required=True,
        help="URL for the API endpoint."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help="API key for authentication."
    )
    parser.add_argument(
        "--model_name",
        type=str,
        required=True,
        help="Name of the model to be evaluated"
    )
    parser.add_argument(
        "--frame_count",
        type=int,
        default=32,
        help="Number of video frames input to the model"
    )
    parser.add_argument(
        "--with_cot",
        action="store_true",
        default=False,
        help="If given, use cot prompting to evaluate the model"
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
    # samples = load_MMR_V()
    samples = load_dataset("JokerJan/MMR-VBench", split='test')

    if args.with_cot:
        save_file = f'your_local_path/MMR-V/results/{args.model_name}_on_MMR_V_cot.json'
    else:
        save_file = f'your_local_path/MMR-V/results/{args.model_name}_on_MMR_V.json'

    visual_path = f'your_local_path/MMR-V/videos'            
    
    results = []
    id_set = set()
    id2sample = {}
    if args.continue_eval:
        if os.path.isfile(save_file):
            print(f"Continue eval from file {save_file}")
            results = read_json(save_file)
            results = [elem for elem in results if elem[f"{args.model_name}_raw_response"] is not None and elem[f"{args.model_name}_raw_response"] != '']
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
        model_version=args.model_name,
        api_type='openai',
        api_key=args.api_key,
        api_url=args.api_url,
        default_headers={"x-foo": "true"},
        max_num_frames=args.frame_count,
    )

    for idx,sample in enumerate(samples):
        
        curr_id = get_unique_id(sample)
        if curr_id in id_set and id2sample[curr_id][f"{args.model_name}_raw_response"] is not None and id2sample[curr_id][f"{args.model_name}_raw_response"] != '':
            continue

        print(f"******** idx={idx} **********")
        
        video_path = os.path.join(visual_path,sample["video"])
        question = sample["question"]
        options = sample["options"]
        
        if args.with_cot:
            full_prompt = cot_prompt_template.format(
                question=question,
                options=options,
            )
        else:
            full_prompt = prompt_template.format(
                question=question,
                options=options,
            )
        response = client.generate(
            visuals=video_path,
            contexts=f'{full_prompt} {VIDEO_TOKEN}'
        )
        print(response)
        sample[f"{args.model_name}_raw_response"] = response

        if isinstance(response, str):
            json_regex = r'\[\[([A-L])\]\]'
            match = re.search(json_regex, response)
            if match:
                final_answer = match.group(1)
                sample[f"{args.model_name}_response"] = {"final_answer": final_answer}
                print(f"Extracted answer: {final_answer}")
            else:
                box_regex = r'\\boxed\{([A-L])\}'
                box_match = re.search(box_regex, response)
                if box_match:
                    final_answer = box_match.group(1)
                    sample[f"{args.model_name}_response"] = {"final_answer": final_answer}
                    print(f"Extracted answer from boxed pattern: {final_answer}")
                else:
                    option = extract_last_option(response)
                    if option:
                        sample[f"{args.model_name}_response"] = {"final_answer": option}
                    else:
                        print("No matching answer found in response.")
                        # 仍然存储原始响应以便检查
                        sample[f"{args.model_name}_raw_response"] = response
        else:
            print("Invalid response type received.")
            sample[f"{args.model_name}_raw_response"] = "Error: Invalid response type"

        results.append(sample)
        # Write the results to the output file
        write_to_json(results, save_file, indent=4)

    eval_logger.info(f"Successfully wrote {len(results)} results to {save_file}!")
    eval_logger.info("Finished Running!")
