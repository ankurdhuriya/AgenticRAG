from typing import TypedDict


class AgentState(TypedDict):
    """Agent state dictionary."""

    question: str  # The user's question
    grades: list[str]  # The grades of the retrieved documents
    llm_output: str  # The output of the LLM model
    documents: list[str]  # The retrieved documents
    loop_count: int  # The number of times the loop has been executed
