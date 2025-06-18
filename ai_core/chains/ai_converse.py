import ollama
from langchain.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.utilities import GoogleSearchAPIWrapper

# Local implementations
from ai_core.config.ai_config import ai_services_config, get_ollama_load_config

OLLAMA_CONFIG = get_ollama_load_config()

ollama_client = ollama.Client(host="localhost", port=11434)
ollama_model = ChatOllama(model="llama2",
                          model_path="models/llama2",
                          temperature=OLLAMA_CONFIG.temperature,
                          num_predict=OLLAMA_CONFIG.num_predict)
