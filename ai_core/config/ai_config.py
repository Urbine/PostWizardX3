import lmstudio as lms
import os
from lmstudio._sdk_models import GpuSetting
from typing import Optional


# TODO: Find a way to modify the SystemPrompt struct to inject a custom system prompt to the session.
MODEL_ID = "l3.1-dark-reasoning-dark-planet-hermes-r1-uncensored-horror-imatrix-max-8b"


def struct_to_dict(obj):
    """Convert an object's struct fields to a dictionary"""
    if hasattr(obj, "__struct_fields__"):
        fields = obj.__struct_fields__
        return {field: getattr(obj, field) for field in fields if hasattr(obj, field)}
    return obj.__dict__


class InferenceParams(lms.LlmPredictionConfig):
    """
    This class contains parameters for model inference.
    """

    max_tokens: Optional[int | bool] = 400
    temperature: Optional[float] = 0.85
    top_k_sampling: Optional[int] = 50
    top_p_sampling: Optional[float | bool] = 0.94
    min_p_sampling: Optional[float | bool] = 0.10
    repeat_penalty: Optional[float | bool] = 1.2
    cpu_threads: Optional[int] = os.cpu_count() // 2
    draft_model: Optional[str] = None


class GPUParams(GpuSetting):
    ratio = 1.0


class LoadModelConfig(lms.LlmLoadModelConfig):
    """
    Detailed description of the class, its purpose, and usage.

    LoadModelConfig is designed to encapsulate configuration settings for loading and managing models.
    It provides default values for various parameters that are commonly used in model training and inference processes.

    """

    gpu = struct_to_dict(GPUParams())
    context_length: Optional[int] = 4096
    eval_batch_size: Optional[int] = 512
    flash_attention: Optional[bool] = False
    keep_model_in_memory: Optional[bool] = True
    seed: Optional[float] = -1
    use_fp16_for_kv_cache: Optional[bool] = False
    try_mmap: Optional[bool] = True


def get_inference_params():
    return struct_to_dict(InferenceParams())


def get_load_model_config():
    return struct_to_dict(LoadModelConfig())
