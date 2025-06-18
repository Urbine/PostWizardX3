"""
This module contains configuration parameters for AI-driven workflows.


Author: Yoham Gabriel B. GitHub@Urbine
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel B. GitHub@Urbine"
__author_email__ = "yohamg@programmer.net"

import os
from typing import Optional, Sequence

# Third-party libraries
import lmstudio as lms
import ollama
from lmstudio._sdk_models import GpuSetting

# Local implementations
from core import ai_services_conf, singleton

ai_services_config = ai_services_conf()
# TODO: Find a way to modify the SystemPrompt struct to inject a custom system prompt to the session.
MODEL_ID = ai_services_config.llm_model_tag
LLM_PROVIDER = ai_services_config.llm_provider
HOST = ai_services_config.llm_serve_host
PORT = ai_services_config.llm_serve_port


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

    max_tokens: Optional[int | bool] = None
    temperature: Optional[float] = None
    top_k_sampling: Optional[int] = None
    top_p_sampling: Optional[float | bool] = None
    min_p_sampling: Optional[float | bool] = None
    repeat_penalty: Optional[float | bool] = None
    cpu_threads: Optional[int] = None
    draft_model: Optional[str] = None


class GPUParams(GpuSetting):
    """
    A class representing GPU parameters used for computing.
    This class provides settings related to GPU performance, including a ratio that determines the degree of optimization applied to computations on the GPU.
    """

    ratio = None


class LoadModelConfig(lms.LlmLoadModelConfig):
    """
    Detailed description of the class, its purpose, and usage.

    LoadModelConfig is designed to encapsulate configuration settings for loading and managing models.
    It provides default values for various parameters that are commonly used in model training and inference processes.

    """

    gpu = struct_to_dict(GPUParams())
    context_length: Optional[int] = None
    eval_batch_size: Optional[int] = None
    flash_attention: Optional[bool] = None
    keep_model_in_memory: Optional[bool] = None
    seed: Optional[float] = -1
    use_fp16_for_kv_cache: Optional[bool] = None
    try_mmap: Optional[bool] = None


@singleton
class OllamaLoadConfig(ollama.Options):
    """
    This class contains configuration parameters for the Ollama client.
    This class contains various parameters that can be used at runtime to customize the behavior of the Ollama model when generating text.
    """

    # load time options
    numa: Optional[bool] = None
    num_ctx: Optional[int] = None
    num_batch: Optional[int] = None
    num_gpu: Optional[int] = None
    main_gpu: Optional[int] = None
    low_vram: Optional[bool] = None
    f16_kv: Optional[bool] = None
    logits_all: Optional[bool] = None
    vocab_only: Optional[bool] = None
    use_mmap: Optional[bool] = None
    use_mlock: Optional[bool] = None
    embedding_only: Optional[bool] = None
    num_thread: Optional[int] = None

    # runtime options
    num_keep: Optional[int] = None
    seed: Optional[int] = None
    num_predict: Optional[int] = None
    top_k: Optional[int] = None
    top_p: Optional[float] = None
    tfs_z: Optional[float] = None
    typical_p: Optional[float] = None
    repeat_last_n: Optional[int] = None
    temperature: Optional[float] = None
    repeat_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    mirostat: Optional[int] = None
    mirostat_tau: Optional[float] = None
    mirostat_eta: Optional[float] = None
    penalize_newline: Optional[bool] = None
    stop: Optional[Sequence[str]] = None


def get_inference_params():
    return struct_to_dict(
        InferenceParams(
            max_tokens=400,
            temperature=0.85,
            top_k_sampling=50,
            top_p_sampling=0.94,
            min_p_sampling=0.10,
            repeat_penalty=1.2,
            cpu_threads=6,
            draft_model=None,
        )
    )


def get_load_model_config():
    gpu_ratio = GPUParams()
    gpu_ratio.ratio = 1.0
    return struct_to_dict(
        LoadModelConfig(
            gpu=gpu_ratio,
            context_length=4096,
            eval_batch_size=128,
            flash_attention=False,
            keep_model_in_memory=True,
            seed=-1,
            use_fp16_for_kv_cache=False,
            try_mmap=True,
        )
    )


def get_ollama_load_config():
    return OllamaLoadConfig(
        num_ctx=4096,         # Larger context for better accuracy (reduce if VRAM limited)
        num_batch=16,         # Reasonable batch size to balance throughput and latency
        num_gpu=1,
        main_gpu=0,           # Assuming you have the primary GPU 0
        low_vram=False,       # Set True if you see OOM errors
        f16_kv=True,          # Use half-precision key-values for better performance
        use_mmap=True,        # Enable memory-mapped files for faster load times
        use_mlock=True,       # Leave off unless you're sure you want to pin in RAM
        embedding_only=False,
        num_thread=os.cpu_count(),  # Matches your physical cores
        # --- Runtime configs ---
        temperature=0.7,            # Balance between randomness and coherence
        top_k=40,                   # Good balance for diversity
        top_p=0.9,                  # Nucleus sampling for controlled creativity
        repeat_penalty=1.1,         # Reduce likelihood of repetition
        repeat_last_n=64,           # Consider last 64 tokens for repetition penalty
        num_predict=256,            # Adjust as needed for your task
        mirostat=0,                 # Use standard sampling unless you need dynamic control
    )
