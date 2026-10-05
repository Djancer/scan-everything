from config import Settings

from .base import LLMProvider
from .mock_provider import MockLLMProvider
from .local_provider import LocalMetadataProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAICompatibleProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == 'ollama':
        return OllamaProvider(settings.ollama_base_url, settings.ollama_model, settings.ollama_timeout)
    if settings.llm_provider == 'local':
        return LocalMetadataProvider()
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
    return OpenAICompatibleProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url,
    )
