# ref: https://github.com/opendatalab/LOKI/blob/main/lm_evaluate/models/qwen_vl_api.py
import re
import base64
import os
import time
import requests as url_requests
import requests

from loguru import logger as eval_logger

try:
    import openai
except Exception as e:
    eval_logger.debug(
        f"Please install openai packages to use GPT and other models compatible with openai's api protocols\n{e}")

import PIL
import numpy as np

try:
    import dashscope
except:
    eval_logger.debug("Can not import Dashscope")

from io import BytesIO
from typing import List, Union
from copy import deepcopy

from decord import VideoReader, cpu
from PIL import Image

from utils.llm_apis.model import  LMM
from utils.llm_apis.registry import register_model

API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = os.getenv("DASHSCOPE_API_KEY", None)

IMAGE_TOKEN = "<image>"
VIDEO_TOKEN = "<video>"

NUM_SECONDS_TO_SLEEP = 30

import base64

def encode_base64_content_from_local(file_path: str) -> str:
    """Encode content from a local file to base64 format."""
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
            encoded_content = base64.b64encode(content).decode('utf-8')
            return encoded_content
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except IOError:
        raise IOError(f"An I/O error occurred while reading the file '{file_path}'.")

def encode_base64_content_from_url(content_url: str) -> str:
    """Encode a content retrieved from a remote url to base64 format."""

    with requests.get(content_url) as response:
        response.raise_for_status()
        result = base64.b64encode(response.content).decode('utf-8')

    return result


@register_model("qwen-vl-api")
class QwenVLAPI(LMM):
    supported_modalities = ["video", "image", "text"]

    def __init__(
            self,
            model_version: str = "qwen-vl-max-0809",
            api_url: str = API_URL,
            timeout: int = 120,
            tmp_folder: str = "./tmp",  # Due to qwen's api restriction,
    ) -> None:

        self.model_version = model_version
        self.api_url = api_url

        self.timeout = timeout
        self.tmp_folder = tmp_folder

        self.headers = {
            "Authorization": "EMPTY",
            "Content-Type": "application/json",
        }

    def prepare_model(self):
        if "vl" not in self.model_version:
            self.supported_modalities = ["text"]

        self.prepared = True
        eval_logger.info(f"Qwen-VL-API activated. API_URL: {self.api_url}. MODEL_VERSION: {self.model_version}")

    def _prepare_generate_kwargs(self, payload, generate_kwargs):
        if "max_new_tokens" in generate_kwargs:
            payload["max_tokens"] = generate_kwargs["max_new_tokens"]
        if "temperature" in generate_kwargs:
            payload["temperature"] = generate_kwargs["temperature"]
        if "top_p" in generate_kwargs:
            payload["top_p"] = generate_kwargs["top_p"]
        if "num_beams" in generate_kwargs:
            payload["num_beams"] = generate_kwargs["num_beams"]

        return payload

    def generate(
            self,
            visuals: Union[Image.Image, str, List[Union[Image.Image, str]]],
            contexts: str,
            **generate_kwargs
    ) -> str:
        """
        Note!!!!!!!!!!!!!! only single video input is supported currently!!!!!!!!!!!!!!!!!!
        :param visuals:
        contexts: Prompt text.
        generate_kwargs: Generation kwargs. Currently we only support greedy decoding.
        Return:
            A piece of response text
        """
        imgs = []
        videos = []

        if isinstance(visuals, str):
            video_base64 = encode_base64_content_from_local(visuals)
            videos.append(video_base64)
        else:
            raise ValueError(f"Only str type visuals are supported! But type {type(visuals)} detected!")

        # image_idx = 0
        #
        # if isinstance(visuals, list):
        #     for visual in visuals:
        #         if isinstance(visual, str):
        #             videos.append(visual)
        #         elif isinstance(visual, Image.Image):
        #             visual.save(os.path.join(self.tmp_folder, f"tmp_{image_idx}_{self.rank}_{self.world_size}.jpg"))
        #             imgs.append(f"tmp_{image_idx}_{self.rank}_{self.world_size}.jpg")
        #             image_idx += 1
        #         else:
        #             error_msg = f"Expected visual type to be Image.Image or str. Got: {type(visual)}"
        #             eval_logger.error(TypeError(error_msg))
        # elif isinstance(visuals, str):
        #     videos.append(visuals)
        #
        # elif isinstance(visuals, Image.Image):
        #     visuals.save(os.path.join(self.tmp_folder, f"tmp_{image_idx}_{self.rank}_{self.world_size}.jpg"))
        #     imgs.append(f"tmp_{image_idx}_{self.rank}_{self.world_size}.jpg")
        #     image_idx += 1

        # Construct messages for request

        # First, convert video place holders to image place holders according to max_num_frames

        messages = []

        if contexts.count(IMAGE_TOKEN) < len(imgs):
            eval_logger.warning(
                f"Provided image tokens and the actual number of images are mismatched! Contexts: {contexts}. Image token num: {contexts.count(IMAGE_TOKEN)}. Number of images: {len(imgs)}")
            contexts = f"{IMAGE_TOKEN} " * (len(imgs) - (contexts.count(IMAGE_TOKEN))) + contexts

        if contexts.count(VIDEO_TOKEN) < len(videos):
            eval_logger.warning(
                f"Provided video tokens and the actual number of videos are mismatched! Contexts: {contexts}. Image token num: {contexts.count(VIDEO_TOKEN)}. Number of images: {len(videos)}")
            contexts = f"{VIDEO_TOKEN} " * (len(videos) - (contexts.count(IMAGE_TOKEN))) + contexts

        contexts = re.split(r'(<video>|<image>)', contexts)
        contexts = [context for context in contexts if context]

        response_json = {"role": "user", "content": []}

        messages.append(deepcopy(response_json))

        image_idx = 0
        video_idx = 0
        for context in contexts:
            if context == "<image>":
                messages[0]["content"].append({"type": "image_url", "image": imgs[image_idx]})
                image_idx += 1
            elif context == "<video>":
                messages[0]["content"].append({"type": "video_url", "video_url": f"data:video/mp4;base64,{videos[video_idx]}"})
                video_idx += 1
            else:
                messages[0]["content"].append({"type": "text", "text": context})

        payload = {"messages": messages}
        payload["model"] = self.model_version
        payload = self._prepare_generate_kwargs(payload, generate_kwargs)

        for attempt in range(5):
            try:
                response = url_requests.post(self.api_url, headers=self.headers, json=payload, timeout=self.timeout)
                eval_logger.debug(response)
                response_data = response.json()
                response_text = response_data["choices"][0]["message"]["content"].strip()
                break  # If successful, break out of the loop

            except Exception as e:
                try:
                    error_msg = response.json()
                except:
                    error_msg = ""

                eval_logger.info(f"Attempt {attempt + 1} failed with error: {str(e)}.\nResponse: {error_msg}.")
                contents = [content for content in payload["messages"][0]["content"] if content["type"] == "text"]
                eval_logger.debug(f"Content: {contents}")
                if attempt < 4:
                    time.sleep(NUM_SECONDS_TO_SLEEP)
                else:  # If this was the last attempt, log and return empty string
                    eval_logger.error(f"All 5 attempts failed. Last error message: {str(e)}.\nResponse: {error_msg}")
                    response_text = ""


        return response_text

