from langchain_groq import ChatGroq
from app.config.settings import Settings

settings = Settings() 


def get_llm(temperature: float = 0.0) -> ChatGroq:
    """Get the LLM model. TO-DO: Make model agnostic."""
    llm = ChatGroq(
        model=settings.MODEL_NAME,  # TO-DO: Make this model agnostic
        temperature=temperature,
        max_tokens=None,
        timeout=None,
        max_retries=3,
    )
    return llm
