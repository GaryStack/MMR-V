import sys
import os
from utils import read_json
import random

def load_MMR_V_4o_error():
    
    file_paths = [
        "/netdisk/zhukejian/MMR_V/MMR-V - 4o - wrong.json",
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

def load_MMR_V():
    file_paths = [
        # "/mnt/userdata/MMR_V/MMR-V - video -llava.json"
        #"/netdisk/zhukejian/MMR_V/MMR-V - split.json",
        #"/mnt/userdata/MMR_V/MMR-V - split.json"
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






if __name__ == '__main__':
