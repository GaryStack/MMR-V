
def get_model_name_mapping(use_docker=False):
    # base_path = '/mnt/userdata/huggingface/' if use_docker else '/home/zhuoran/hongbang/huggingface/'
    base_path = '/mnt/publiccache'
    model_name_mapping = {
        "llama2-7b-base": f'{base_path}/hongbang/Llama-2-7b-hf',
        "llama2-13b-base": f'{base_path}/hongbang/Llama-2-13b-hf',
        "llama2-7b-chat": f'{base_path}/hongbang/Llama-2-7b-chat-hf',
        "llama2-13b-chat": f'{base_path}/hongbang/Llama-2-13b-chat-hf',
        'vicuna-7b-v1.5': f'{base_path}/hongbang/vicuna-7b-v1.5',
        'vicuna-13-v1.5': f'{base_path}/hongbang/vicuna-13b-v1.5',
        'llama3-8b' :f'{base_path}/huggingface/Meta-Llama-3-8B',
        'llama3-8b-instruct' :f'{base_path}/huggingface/Meta-Llama-3-8B-Instruct',
        'confucius': f'{base_path}/hongbang/confucius-confidence-verb',
        'mistral-7b-instruct':f'{base_path}/huggingface/Mistral-7B-Instruct-v0.2'
    }
    return model_name_mapping
