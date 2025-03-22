from typing import Literal

from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

from app.core.graph.llm import get_llm
from app.core.graph.prompts import (
    get_answer_prompt,
    get_grade_prompt,
    get_rewrite_prompt,
)
from app.core.graph.state import AgentState
from app.core.vector_db import VectorStore

# Get the LLM model
llm: any = get_llm()


def retrieve_docs(state: AgentState, vector_store: VectorStore) -> AgentState:
    """Retrieve documents based on the question."""
    question = state["question"]
    retriever = vector_store.db.as_retriever()
    documents = retriever.invoke(input=question)
    state["documents"] = [doc.page_content for doc in documents]
    return state


class GradeDocuments(BaseModel):
    """Boolean values to check for relevance on retrieved documents."""

    score: Literal["Yes", "No"] = Field(
        description="Documents are relevant to the question, 'Yes' or 'No'"
    )


def document_grader(state: AgentState) -> AgentState:
    """Grade the retrieved documents."""
    docs = state["documents"]
    question = state["question"]

    grade_prompt = get_grade_prompt()

    # Use the LLM model with a structured output
    structured_llm = llm.with_structured_output(GradeDocuments)
    grader_llm = grade_prompt | structured_llm
    scores = []
    for doc in docs:
        result = grader_llm.invoke({"document": doc, "question": question})
        scores.append(result.score)
    state["grades"] = scores
    return state


def rewriter(state: AgentState) -> AgentState:
    """Rewrite the question."""
    question = state["question"]

    re_write_prompt = get_rewrite_prompt()

    # Use the LLM model with a string output parser
    question_rewriter = re_write_prompt | llm | StrOutputParser()
    output = question_rewriter.invoke({"question": question})
    state["question"] = output
    state["loop_count"] += 1
    return state


def generate_answer(state: AgentState) -> AgentState:
    """Generate an answer based on the question and context."""
    question = state["question"]
    context = state["documents"]

    prompt = get_answer_prompt()
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"question": question, "context": context})
    state["llm_output"] = result
    return state


def off_topic_response(state: AgentState) -> AgentState:
    """Handle an off-topic response."""
    state["llm_output"] = "I cant respond to that!"
    return state


def gen_router(state: AgentState) -> str:
    """Determine the next step in the workflow."""
    grades = state["grades"]
    loop_count = state["loop_count"]

    if any(grade.lower() == "yes" for grade in grades):
        return "generate"
    elif loop_count > 1:  # Switch to general AI after 2 rewrite
        print("GOING to OFF TOPIC")
        return "off_topic_response"
    else:
        return "rewrite_query"


# Create a state graph
workflow = StateGraph(AgentState)

# Create a vector store
vector_store = VectorStore()

# Add nodes to the workflow
workflow.add_node("retrieve_docs", lambda state: retrieve_docs(state, vector_store))
workflow.add_node("document_grader", document_grader)
workflow.add_node("rewrite_query", rewriter)
workflow.add_node("generate_answer", generate_answer)
workflow.add_node("off_topic_response", off_topic_response)

# Add edges to the workflow
workflow.add_edge("retrieve_docs", "document_grader")

# Add conditional edges to the workflow
workflow.add_conditional_edges(
    "document_grader",
    gen_router,
    {
        "generate": "generate_answer",
        "rewrite_query": "rewrite_query",
        "off_topic_response": "off_topic_response",
    },
)
workflow.add_edge("rewrite_query", "retrieve_docs")
workflow.add_edge("generate_answer", END)
workflow.add_edge("off_topic_response", END)

# Set the entry point of the workflow
workflow.set_entry_point("retrieve_docs")

# Compile the workflow
graph = workflow.compile()


async def generate_response(questions):
    """Generate responses for multiple questions using the workflow."""
    result = []
    for question in questions:
        output = await graph.ainvoke({"question": question, "loop_count": 0})
        result.append({"question": question, "answer": output["llm_output"]})
    return result
