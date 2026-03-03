# app/pipeline/extractor/__init__.py
import logging
from .base import BaseExtractor
from .llm_extractor import LLMExtractor
from .mock_extractor import MockExtractor
import os

logger = logging.getLogger(__name__)

def get_extractor(use_mock: bool = False, provider: str = "openai") -> BaseExtractor:
    """
    Factory to switch between real LLM and Mock data, and different providers.
    """
    if use_mock:
        logger.info("Initializing MockExtractor")
        return MockExtractor()
        
    if provider == "openai":                
        logger.info(f"Initializing LLMExtractor with OpenAI provider (Model: {os.environ.get('OPENAI_MODEL', 'gpt-4o')})")
        api_key = os.environ.get("OPENAI_API_KEY")
        model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        return LLMExtractor(api_key=api_key, model=model)
    
    # ... handle other providers ...
    
    raise ValueError(f"Unknown provider: {provider}")