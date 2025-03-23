from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.config.settings import Settings
from typing import Union

settings = Settings()


def get_llm(temperature: float = 0.0) -> Union[ChatGroq, ChatOpenAI]:
    """Get the LLM model"""

    if settings.OPENAI_API_KEY:
        return ChatOpenAI(
            model=settings.MODEL_NAME.get('gpt'),
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=3,
        )

    return ChatGroq(
        model=settings.MODEL_NAME.get('llama'),
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=3,
    )
