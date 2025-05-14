from typing import Union, Literal
# from langchain.chat_models import ChatOpenAI
# # from langchain import OpenAI
# from langchain.llms import OpenAI
# from langchain.schema import (
#     HumanMessage
# )
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from utils.config_utils import get_model_name_mapping
import warnings
import os


class AnyOpenAILLM:
    def __init__(self, *args, **kwargs):
        # Determine model type from the kwargs
        model_name = kwargs.get('model_name', 'gpt-3.5-turbo')
        if model_name.split('-')[0] == 'text':
            self.model = OpenAI(*args, **kwargs)
            self.model_type = 'completion'
        else:
            self.model = ChatOpenAI(*args, **kwargs)
            self.model_type = 'chat'

    def __call__(self, prompt: str):
        if self.model_type == 'completion':
            return self.model(prompt)
        else:
            return self.model(
                [
                    HumanMessage(
                        content=prompt,
                    )
                ]
            ).content


def load_hf_tokenizer(
        model_name_or_path,
        tokenizer_name_or_path=None,
        use_fast_tokenizer=True,
        padding_side="left",
        token=os.getenv("HF_TOKEN", None),
        use_docker=False,
):
    from transformers import AutoTokenizer

    model_name_mapping = get_model_name_mapping(use_docker)
    if model_name_or_path not in model_name_mapping.keys():
        print(f"{model_name_or_path} not in pre-defined tokenizers!")
        print("Note whether this is the desired behaviour!")
        print(f"Loading tokenizers from {model_name_or_path}...")
    else:
        model_name_or_path = model_name_mapping[model_name_or_path]
        print(f"Load pre-defined tokenizers from {model_name_or_path}...")

    # # Need to explicitly import the olmo tokenizer.
    # try:
    #     from hf_olmo import OLMoTokenizerFast
    # except ImportError:
    #     warnings.warn("OLMo not installed. Ignore if using a different model.")

    if not tokenizer_name_or_path:
        tokenizer_name_or_path = model_name_or_path
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path, use_fast=use_fast_tokenizer, token=token)
    except:
        # some tokenizers (e.g., GPTNeoXTokenizer) don't have the slow or fast version, so we just roll back to the default one
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name_or_path, token=token)
    # set padding side to left for batch generation
    tokenizer.padding_side = padding_side
    # set pad token to eos token if pad token is not set (as is the case for llama models)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    return tokenizer

def load_hf_lm(
        model_name_or_path,
        device_map="auto",
        torch_dtype="auto",
        load_in_8bit=False,
        load_in_4bit=False,
        convert_to_half=False,
        gptq_model=False,
        token=os.getenv("HF_TOKEN", None),
        use_docker=False,
        skip_map=False,
):
    model_name_mapping = get_model_name_mapping(use_docker)
    if model_name_or_path not in model_name_mapping.keys():
        print(f"{model_name_or_path} not in pre-defined models!")
        print("Note whether this is the desired behaviour!")
        print(f"Loading models from {model_name_or_path}...")
    else:
        model_name_or_path = model_name_mapping[model_name_or_path]
        print(f"Load pre-defined models from {model_name_or_path}...")


    # if not skip_map:
    #     model_name_mapping = get_model_name_mapping(use_docker)
    #     if model_name_or_path not in model_name_mapping.keys():
    #         raise ValueError(f"{model_name_or_path} not in pre-defined models!")
    #     model_name_or_path = model_name_mapping[model_name_or_path]
    # else:
    #     print("Please check whether this is the desired behaviour!")
    #     print(f"Loading model from local dir {model_name_or_path}!")

    # Loading OLMo models from HF requires `trust_remote_code=True`.
    # TODO: Implement this via command-line flag rather than hardcoded list.
    trusted_models = ["allenai/OLMo-7B", "allenai/OLMo-7B-Twin-2T", "allenai/OLMo-1B"]
    # if model_name_or_path in trusted_models:
    #     trust_remote_code = True
    # else:
    #     trust_remote_code = False
    trust_remote_code = False

    from transformers import AutoModelForCausalLM, AutoTokenizer, OPTForCausalLM, GPTNeoXForCausalLM
    if gptq_model:
        from auto_gptq import AutoGPTQForCausalLM
        model_wrapper = AutoGPTQForCausalLM.from_quantized(
            model_name_or_path, device="cuda:0", use_triton=True, trust_remote_code=trust_remote_code
        )
        model = model_wrapper.model
    elif load_in_8bit:
        model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            device_map=device_map,
            load_in_8bit=True,
            token=token,
            trust_remote_code=trust_remote_code
        )
    elif load_in_4bit:
        from transformers import BitsAndBytesConfig
        print("Load model in 4-bit quantization...")
        bnb_config = BitsAndBytesConfig(load_in_4bit=True)
        return AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            quantization_config=bnb_config,
            torch_dtype=torch.bfloat16,
            device_map=device_map,
            token=token,
            trust_remote_code=trust_remote_code,
        )
    else:
        if device_map:
            model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                device_map=device_map,
                torch_dtype=torch_dtype,
                token=token,
                trust_remote_code=trust_remote_code,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                torch_dtype=torch_dtype,
                token=token,
                trust_remote_code=trust_remote_code,
            )
            if torch.cuda.is_available():
                model = model.cuda()
        if convert_to_half:
            model = model.half()
    if model.config.pad_token_id is None:
        model.config.pad_token_id = model.config.eos_token_id
    model.eval()
    return model

def load_model_and_tokenizer(model_name, use_docker):
    model_name_mapping = get_model_name_mapping(use_docker)
    if model_name not in model_name_mapping.keys():
        raise ValueError(f"{model_name} not in pre-defined models!")
    model_name_or_path = model_name_mapping[model_name]
    model, tokenizer = load_llama_model_and_tokenizer(model_name_or_path)
    return model, tokenizer


def load_llama_model_and_tokenizer(model_name_or_path):
    # load models
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        torch_dtype=torch.float16,
        device_map='balanced',
    ).eval()

    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        trust_remote_code=True,
        use_fast=False
    )
    tokenizer.pad_token = tokenizer.unk_token
    tokenizer.padding_side = 'left'

    return model, tokenizer


def load_llama_tokenizer(model_name_or_path):
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        trust_remote_code=True,
        use_fast=False
    )
    tokenizer.pad_token = tokenizer.unk_token
    tokenizer.padding_side = 'left'

    return tokenizer
