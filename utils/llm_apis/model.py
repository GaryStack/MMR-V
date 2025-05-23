from abc import ABC, abstractmethod
from typing import Union, List

from PIL import Image


class LMM(ABC):
    prepared = False
    supported_modalities = []
    _rank = 0
    _world_size = 1
    support_batching = False

    def __init__(self):
        """
        Defines the base model class.
        All models should be able to do:
            1. Prepare model for evaluation, i.e., load huggingface checkpoints or prepare api credentials.
            2. Generate texts based on provided visuals and contexts.
        """
        self._model = None
        self._rank = 0  # For MultiGPU Inference
        self._world_size = 1  # For MultiGPU Inference

    @abstractmethod
    def prepare_model(self):
        pass

    @abstractmethod
    def generate(
            self,
            visuals: Union[Image.Image, List[Image.Image], str, List[str]],
            contexts: Union[str, List[str]],
            **kwargs
    ):
        pass

    @property
    def rank(self):
        return self._rank

    @property
    def world_size(self):
        return self._world_size