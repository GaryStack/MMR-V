import os
import openai
import time
import numpy as np
import logging
import sys

import base64
import time
from io import BytesIO
from typing import Union

from openai import AzureOpenAI, OpenAI
from openai.types.chat import ChatCompletionContentPartParam, ChatCompletionMessageParam
from PIL import Image

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT



# build claude class
class Claude_Model():
    def __init__(self,
            client,
            model="claude-3-5-haiku-20241022",
            temperature=0,
            max_tokens=1024,
            n=1,
            patience=1000000,
            sleep_time=2,
        ):
        self.client = client
        self.model = model
        self.use_image = True if "vision" in model else False
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n = n
        self.patience = patience
        self.sleep_time = sleep_time

    def get_response_with_image(self, user_prompt, image1, image2):
        patience = self.patience
        max_tokens = self.max_tokens

        user_messages: list = []

        for decoded_image in [image1, image2]:
            user_messages.append(
                {
                    "type": "image",
                    "source":{
                        "type": "base64",
                        "media_type": "image/png",
                        "data": decoded_image,
                    },
                }
            )

        user_messages.append({"type": "text", "text": user_prompt})

        messages: list = [
            {"role": "user", "content": user_messages},
        ]

        while patience > 0:
            patience -= 1
            try:
                response = self.client.messages.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                )
                # predictions = [choice.message.content for choice in response.choices]
                # prediction = predictions[0]
                prediction = response.content[0].text

                if prediction != "" and prediction is not None:
                    return prediction.strip()

            except Exception as e:
                print(e)

                if "Please reduce the length of the messages or completion" in str(e):
                    max_tokens = int(max_tokens * 0.9)
                    print("!!Reduce max_tokens to", max_tokens)
                if max_tokens < 8:
                    return ""
                if "Please reduce the length of the messages." in str(e):
                    print("!!Reduce user_prompt to", user_prompt[:-1])
                    return ""
                if self.sleep_time > 0:
                    print(f"Sleeping for {self.sleep_time} seconds")
                    time.sleep(self.sleep_time)

        return ""


# class OpenAIModel:
#     def __init__(self, model_name, key_name="API_KEY"):
#         self.model_name = model_name
#         self.key_name = key_name
#
#     def load_model(self):
#         key_name = self.key_name
#         if os.getenv(key_name):
#             api_key = os.environ[key_name]
#             print(f"loading API key name {key_name} from environment!")
#         else:
#             assert ValueError(f"Could not find {key_name} in the environment!")


# build gpt class
class GPT_Model:
    def __init__(
        self,
        client: Union[OpenAI, AzureOpenAI],
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=1024,
        n=1,
        patience=1000000,
        sleep_time=2,
    ):
        self.client = client
        self.model = model
        self.use_image = True if "vision" in model else False
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.n = n
        self.patience = patience
        self.sleep_time = sleep_time

    def get_response_with_image(self,user_prompt,image1,image2):
        patience = self.patience
        max_tokens = self.max_tokens

        user_messages: list[ChatCompletionContentPartParam] = []

        for decoded_image in [image1,image2]:
            user_messages.append(
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{decoded_image}"}}
            )

        user_messages.append({"type": "text", "text": user_prompt})

        messages: list[ChatCompletionMessageParam] = [
            {"role": "user", "content": user_messages},
        ]

        while patience > 0:
            patience -= 1
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    n=self.n,
                )
                predictions = [choice.message.content for choice in response.choices]
                prediction = predictions[0]

                if prediction != "" and prediction is not None:
                    return prediction.strip()

            except Exception as e:
                print(e)

                if "Please reduce the length of the messages or completion" in str(e):
                    max_tokens = int(max_tokens * 0.9)
                    print("!!Reduce max_tokens to", max_tokens)
                if max_tokens < 8:
                    return ""
                if "Please reduce the length of the messages." in str(e):
                    print("!!Reduce user_prompt to", user_prompt[:-1])
                    return ""
                if self.sleep_time > 0:
                    print(f"Sleeping for {self.sleep_time} seconds")
                    time.sleep(self.sleep_time)

        return ""

    def get_response(self, user_prompt: str, decoded_image: Union[Image.Image, None] = None):
        patience = self.patience
        max_tokens = self.max_tokens

        user_messages: list[ChatCompletionContentPartParam] = []

        if self.use_image:
            if decoded_image is None:
                print(
                    f'You are using a model that supports vision: {self.model}, '
                    f'but no image was provided when generating a response. This is likely unintended.'
                )
            else:
                buffered = BytesIO()
                decoded_image.save(buffered, format="PNG")
                base64_image_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                user_messages.append(
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image_str}"}}
                )

        user_messages.append({"type": "text", "text": user_prompt})

        messages: list[ChatCompletionMessageParam] = [
            {"role": "user", "content": user_messages},
        ]

        while patience > 0:
            patience -= 1
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    n=self.n,
                )

                predictions = [choice.message.content for choice in response.choices]
                prediction = predictions[0]

                if prediction != "" and prediction is not None:
                    return prediction.strip()

            except Exception as e:
                print(e)

                if "Please reduce the length of the messages or completion" in str(e):
                    max_tokens = int(max_tokens * 0.9)
                    print("!!Reduce max_tokens to", max_tokens)
                if max_tokens < 8:
                    return ""
                if "Please reduce the length of the messages." in str(e):
                    print("!!Reduce user_prompt to", user_prompt[:-1])
                    return ""
                if self.sleep_time > 0:
                    print(f"Sleeping for {self.sleep_time} seconds")
                    time.sleep(self.sleep_time)

        return ""


def call_ChatGPT(messages, model="gpt-3.5-turbo", **kwargs):
    # call GPT-3 API until result is provided and then return it
    response = None
    received = False
    num_rate_errors = 0
    while not received:
        try:
            response = openai.chat.completions.create(
                messages=messages,
                model=model,
                **kwargs,
            )
            received = True
        except:
            # print(message)
            num_rate_errors += 1
            error = sys.exc_info()[0]
            # if error == openai.error.InvalidRequestError:
            #     # something is wrong: e.g. prompt too long
            #     logging.critical(f"InvalidRequestError\nPrompt passed in:\n\n{message}\n\n")
            #     # assert False
            #     raise error

            logging.error("API error: %s (%d). Waiting %dsec" % (error, num_rate_errors, np.power(2, num_rate_errors)))
            time.sleep(np.power(2, num_rate_errors))
    return response
