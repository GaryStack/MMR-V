from torch.utils.data import Dataset
import numpy as np
import re

def select(samples, **kwargs):
    results = samples[:]  # Make a copy of the original samples

    for k, v in kwargs.items():
        results = [sample for sample in results if sample.get(k) == v]

    return results


# Convert the list of dictionaries to a PyTorch Dataset
class CustomDataset(Dataset):
    def __init__(self, data,*keys):
        if len(keys) == 0:
            keys = list(next(iter(data)).keys())
        data = [
            {key:sample[key] for key in keys}
            for sample in data
        ]
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

def max_indices(arr, k):
    # Use numpy's partition to get the indices of the k largest elements' index
    indices = np.argpartition(arr, -k)[-k:]

    # Sort the indices based on their corresponding values in descending order
    sorted_indices = indices[np.argsort(arr[indices])[::-1]]

    return sorted_indices


def min_indices(arr, k):
    # get the indices of the k smallest elements' index
    return max_indices(-arr, k)

def keep_before_double_newline(text):
    # 使用正则表达式匹配连续两个换行符进行拆分
    lines = re.split(r'\n\n', text, maxsplit=1)
    # 返回第一个连续两个换行符之前的内容
    return lines[0]