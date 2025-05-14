from dotenv import load_dotenv
import os
# 加载 .env 文件中的环境变量
# load_dotenv()
import sys
import re
sys.path.append(os.path.abspath("/netdisk/zhukejian/implicit_video_anonotations"))
sys.path.append(os.path.abspath("/mnt/userdata/implicit_video_anonotations"))
# print(sys.path)

# breakpoint()
# 从环境变量中获取 API 密钥
os.environ['DASHSCOPE_API_KEY'] = 'your_api_key_here'

prompt_template = """
[[INSTRUCTIONS]]
Please select the best answer to the following multiple-choice question based on the video. 
Only one option is the most accurate answer in relation to the question and the video.

What is the correct answer to this question [[QUESTION]]
Options:
[[OPTIONS]]

Let's think step by step.
[[END OF INSTRUCTIONS]]
[[QUESTION]]
{question}
[[END OF QUESTION]]
[[OPTIONS]]
{options}
[[END OF OPTIONS]]
[[OUTPUT FORMAT]]
Format your answer as follows:
[Analyze the best option for question]
[Justification for your final choice based on the thinking process.]

Give the final correct option number in the following format: \"[[A]]\" or \"[[B]]\" or \"[[C]]\" or \"[[D]]\" ...
[[END OF OUTPUT FORMAT]]
"""


api_key = os.getenv('DASHSCOPE_API_KEY')

import os
from utils.video_utils import OpenAI,VIDEO_TOKEN
from utils import write_to_json
from dataset.load_MMR_V import load_MMR_V
if __name__ == '__main__':
    print("Hello World")
    samples = load_MMR_V()
    # samples = load_vcg_bench_diverse_subset()
    model_name = 'Qwen2.5-VL-7B-Instruct'
    save_file = f'/mnt/userdata/implicit_video_anonotations/results/{model_name}_on_MMR_cot.json'
    visual_path = '/mnt/userdata/implicit_video_anonotations/static/videos'
    results = []
    client = OpenAI(
        model_version='/mnt/usercache/zhuoran/rl/Qwen2.5-VL-7B-Instruct',
        api_type='openai',
        api_key=api_key,
        api_url="http://210.75.240.153:22345/v1/chat/completions",
        max_num_frames=8,
    ) 

    # 每次处理一条数据，注意：不再设置 batch
    for idx, sample in enumerate(samples):
        print(f"******** idx={idx} **********")
        video_path = os.path.join(visual_path, sample["video"])
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
            json_regex = r'\[\[([ABCDEFGHIJKL])\]\]'
            match = re.search(json_regex, response)
            if match:
                final_answer = match.group(1)
                sample[f"{model_name}_response"] = {"final_answer": final_answer}
                print(f"Extracted answer: {final_answer}")
            else:
                print("No matching answer found in response.")
                sample[f"{model_name}_raw_response"] = response
        else:
            print("Invalid response type received.")
            sample[f"{model_name}_raw_response"] = "Error: Invalid response type"
        results.append(sample)

        # 将结果写入文件（也可选择每处理一条数据写入一次）
        write_to_json(results, save_file, indent=4)

    eval_logger.info(f"Successfully wrote {len(results)} results to {save_file}!")
    eval_logger.info("Finished Running!")