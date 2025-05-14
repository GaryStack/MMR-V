import sys
import os
sys.path.append(os.path.abspath("/netdisk/zhukejian/AnyReward-master"))
from utils import read_json
import random

def load_MMR_V_4o_error():
    
    file_paths = [
        "/netdisk/zhukejian/implicit_video_anonotations/MMR-V - 4o - wrong.json",
    ]

    samples = None

    for path in file_paths:
        if os.path.exists(path):
            samples = read_json(path)
            print(f"Read data from {path}")
            break  # 一旦找到有效路径，停止遍历

    # 如果没有找到有效路径，抛出错误
    if samples is None:
        raise FileNotFoundError("None of the provided file paths are valid.")

    # breakpoint()
    print(f"Load {len(samples)} samples for the text-audio-to-text preference task.")
    return samples
    # description_file = '/netdisk/zhukejian/VCGBench-Diverse/human_annotated_video_descriptions_vcgbench_diverse_human_annotated_descriptions.json'
    # annotation_descriptions = read_json(description_file)

    # video2description = {elem["video_name"]: elem["description"] for elem in annotation_descriptions}
    # for sample in qa_samples:
    #     video_name = sample["video_name"]
    #     if video_name not in video2description.keys():
    #         # print(video_name)
    #         continue
    #     sample["description"] = video2description[video_name]
    # breakpoint()
    return IVBench_samples

def load_MMR_V():
    file_paths = [
        # "/mnt/userdata/implicit_video_anonotations/MMR-V - video -llava.json"
        "/netdisk/zhukejian/implicit_video_anonotations/MMR-V - split.json",
        "/mnt/userdata/implicit_video_anonotations/MMR-V - split.json"
    ]

    samples = None

    for path in file_paths:
        if os.path.exists(path):
            samples = read_json(path)
            print(f"Read data from {path}")
            break  # 一旦找到有效路径，停止遍历

    # 如果没有找到有效路径，抛出错误
    if samples is None:
        raise FileNotFoundError("None of the provided file paths are valid.")

    # breakpoint()
    print(f"Load {len(samples)} samples for MMR-V.")
    return samples
    # description_file = '/netdisk/zhukejian/VCGBench-Diverse/human_annotated_video_descriptions_vcgbench_diverse_human_annotated_descriptions.json'
    # annotation_descriptions = read_json(description_file)

    # video2description = {elem["video_name"]: elem["description"] for elem in annotation_descriptions}
    # for sample in qa_samples:
    #     video_name = sample["video_name"]
    #     if video_name not in video2description.keys():
    #         # print(video_name)
    #         continue
    #     sample["description"] = video2description[video_name]
    # breakpoint()
    return IVBench_samples






if __name__ == '__main__':
