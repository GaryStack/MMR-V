from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.abspath("/netdisk/zhukejian/implicit_video_anonotations"))
import json
import re
# 加载 .env 文件中的环境变量
# load_dotenv()
# 从环境变量中获取 API 密钥

from loguru import logger as eval_logger
from utils.video_utils import OpenAI,VIDEO_TOKEN
from utils import write_to_json
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
give the final correct option number in the following format: \"[[X]]\"
[[END OF OUTPUT FORMAT]]
"""

if __name__ == '__main__':
    print("Hello World")

    samples = load_MMR_V()
    model_name = 'gemini-2.0-flash'
    save_file = f'/netdisk/zhukejian/implicit_video_anonotations/results/{model_name}_on_MMR_V.json'
    visual_path = '/netdisk/zhukejian/implicit_video_anonotations/static/videos'

    client = OpenAI(
        model_version=model_name,
        api_type='openai',
        api_key=api_key,
        api_url="https://api.gpt.ge/v1/chat/completions",
        default_headers={"x-foo": "true"},
        max_num_frames=512,
    )
    # breakpoint()
    results = []
    for idx,sample in enumerate(samples[:]):
        print(f"******** idx={idx} **********")
        # if idx<848:
        #     continue
        # breakpoint()
        # if idx>=10:
        #     break
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
        # breakpoint()
        # json_regex = r'JSON Output:\s*===\s*(?:```json\s*)?(\{.*?\})\s*(?:```)?\s*===\s*'
        
        # Use findall to match all possible JSON blocks
        # matches = re.findall(json_regex, response, re.DOTALL)

        if isinstance(response, str):
            json_regex = r'\[\[([ABCDEFGHIJKL])\]\]'
            match = re.search(json_regex, response)
            
            if match:
                final_answer = match.group(1)  
                sample[f"{model_name}_response"] = {"final_answer": final_answer}
                print(f"Extracted answer: {final_answer}")
            else:
                print("No matching answer found in response.")
                sample[f"{model_name}_raw_response"] = response  # 仍然存储原始响应以便检查
        else:
            print("Invalid response type received.")
            sample[f"{model_name}_raw_response"] = "Error: Invalid response type"
        results.append(sample)
        # Write the results to the output file
        write_to_json(results, save_file, indent=4)
    eval_logger.info(f"Successfully wrote {len(results)} results to {save_file}!")
    eval_logger.info("Finished Running!")