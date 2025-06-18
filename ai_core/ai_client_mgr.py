"""
This module provides a single function to load the LLM clients based on the configuration.

Author: Yoham Gabriel B. GitHub@Urbine
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel B. GitHub@Urbine"
__author_email__ = "yohamg@programmer.net"

import lmstudio as lms
import ollama

# Local implementations
from core import InvalidAIConfig
from ai_core.config.ai_config import (
    get_load_model_config,
    ai_services_config,
    MODEL_ID,
)


def load_llm_client() -> ollama.Client | lms.Client:
    """Loads the LLM client based on the configuration."""
    if not ai_services_config:
        raise InvalidAIConfig("AI services configuration is not set")

    if ai_services_config.llm_provider == "ollama":
        client_ollama = ollama.Client(
            host=ai_services_config.llm_serve_host,
            port=ai_services_config.llm_serve_port,
        )
        return client_ollama
    elif ai_services_config.llm_provider == "lmstudio":
        client_lms = lms.Client()
        loaded_models = client_lms.list_loaded_models()
        if loaded_models:
            for llm_model in loaded_models:
                llm_model.unload()
        return client_lms
    else:
        raise InvalidAIConfig("AI provider is not supported")


def load_lms_model():
    """
    Loads the LMS model based on the configuration.
    Unloads any previously loaded models to free up GPU memory for the new model.

    :return: ``tuple(lms.llm, model_instance)``
    """
    client_lms = lms.Client()
    loaded_models = client_lms.list_loaded_models()
    if loaded_models:
        for llm_model in loaded_models:
            llm_model.unload()
    model_instance = client_lms.llm.load_new_instance(
        MODEL_ID, config=get_load_model_config()
    )
    return lms.llm(MODEL_ID), model_instance


def load_ollama_model():
    """
    Loads the Ollama client based on the configuration and returns a client instance.
    Users should then call the chat method on the returned client instance to load the model with a prompt.

    :return: ``tuple(client, model_list)``
    """
    client_ollama = load_llm_client()
    return client_ollama, client_ollama.list()


def load_llm_model():
    """
    Load an LLM (Large Language Model) model based on the existing environment.

    This function attempts to load an LLM model using an LMS (Large Models Service) client.
    If the client is an instance of lms.Client, it loads a model from that client.
    If the client is not an instance of lms.Client, it closes the Ollama client and then loads the new model,
    assuming there is a server instance running.

    :return: ``tuple(LMStudio llm, model_instance)`` or ``tuple(Ollama client, model_list)``
    """
    client = load_llm_client()
    if isinstance(client, lms.Client):
        return load_lms_model()
    else:
        # Close the Ollama client to load the new model in case there is a server instance running
        client.close()
        return load_ollama_model()
