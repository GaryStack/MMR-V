import time
from datasets import load_dataset, Dataset, Image, DatasetDict
from dataset.Ours.load_ours import *
from dotenv import load_dotenv
from huggingface_hub import login
import os
load_dotenv()
login(os.environ["HUGGINGFACE_TOKEN"])
from tqdm import tqdm
from huggingface_hub import HfApi

api = HfApi()


# 将 dataset 中的 image 属性从相对路径转换为绝对路径
def resolve_image_path(example):
    example["response1_path"] = example["response1"]
    example["response2_path"] = example["response2"]

    example["response1"] = os.path.join(visual_path,example["response1"])
    example["response2"] = os.path.join(visual_path,example["response2"])

    return example

if __name__ == '__main__':
    print("Hello World!")

    # ti2t
    dataset = load_dataset("json",data_files="/netdisk/zhukejian/implicit_video_anonotations/MMR-V - split.json")
    dataset_dict = DatasetDict({
        "test": dataset["train"]  # 将默认的 train 重命名为 test
    })
    dataset = dataset_dict

    visual_path = '/home/hongbang/projects/ATTBenchmark/results/OmniRewardBench/media_data'


    # dataset = dataset.map(resolve_image_path)

    # dataset = dataset.cast_column("response1", Image(decode=True))
    # dataset = dataset.cast_column("response2", Image(decode=True))

    print("Start pushing...")
    dataset.push_to_hub("HongbangYuan/OmniRewardBench","text_to_video")

    print("Finished Running!")