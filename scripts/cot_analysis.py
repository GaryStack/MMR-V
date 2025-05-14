import json

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main(file1_path, file2_path):
    # 加载两个JSON文件
    data1 = load_json(file1_path)
    data2 = load_json(file2_path)

    # 需要保留的字段列表
    keep_fields = {
        "video", "videoType", "remark", "question",
        "options", "correctAnswer", "abilityType_L2", "abilityType_L3"
    }

    # 创建键集合（video, question）
    def get_key(item):
        return (item["video"], item["question"])

    keys1 = {get_key(item) for item in data1}
    keys2 = {get_key(item) for item in data2}

    # 分类处理数据
    only_in_file1 = []
    only_in_file2 = []
    common = []

    # 处理第一个文件的数据
    for item in data1:
        key = get_key(item)
        filtered = {k: v for k, v in item.items() if k in keep_fields}
        if key not in keys2:
            only_in_file1.append(filtered)
        else:
            common.append(filtered)

    # 处理第二个文件的数据
    for item in data2:
        key = get_key(item)
        filtered = {k: v for k, v in item.items() if k in keep_fields}
        if key not in keys1:
            only_in_file2.append(filtered)

    # 保存结果
    save_json(only_in_file1, 'only_in_zero_shot.json')
    save_json(only_in_file2, 'only_in_cot.json')
    save_json(common, 'common.json')

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("用法：python script.py 文件1.json 文件2.json")
        sys.exit(1)
        
    main(sys.argv[1], sys.argv[2])