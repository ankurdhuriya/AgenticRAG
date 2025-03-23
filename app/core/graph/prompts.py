from langchain_core.prompts.chat import ChatPromptTemplate


def get_grade_prompt() -> ChatPromptTemplate:
    """Get the refined document relevance grading prompt template."""
    system = """You are a precision grading system analyzing document-question relevance. Evaluate whether the document excerpt:
    1. Directly addresses the question's core subject matter
    2. Contains supporting evidence for potential answers
    3. Shares contextual overlap with key entities/relationships
    
    Response Guidelines:
    - "Yes" only if document provides substantive, actionable information
    - "No" for tangential references or incomplete information
    - Consider semantic relationships, not just keyword matches
    - Respond strictly with 'Yes' or 'No' without commentary"""

    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Document Excerpt:\n{document}\n\n"
                "User Query: {question}\n\n"
                "Relevance Judgment (Yes/No):",
            ),
        ]
    )


def get_rewrite_prompt() -> ChatPromptTemplate:
    """Get the enhanced query optimization prompt template."""
    system = """You are a search optimization engine. Improve the query by:
    1. Identifying core semantic intent
    2. Expanding with technical synonyms
    3. Clarifying ambiguous terms
    4. Maintaining original question's context
    
    Output Format:
    - Single natural language question
    - Preserve original language
    - No markdown or special formatting"""

    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Original Question:\n{question}\n\nOptimized Retrieval Query:"),
        ]
    )


def get_answer_prompt() -> ChatPromptTemplate:
    """Get the precision answer generation prompt template."""
    system = """Generate authoritative answers using these rules:
    1. Base response strictly on provided context
    2. Use technical terminology where appropriate
    3. Maintain objective, academic tone
    4. Acknowledge document limitations when present
    5. Structure complex answers with clear reasoning
    
    If context is insufficient, respond: 'The documents do not contain sufficient information to answer this question accurately.'"""

    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Contextual Documents:\n{context}\n\n"
                "Query: {question}\n\n"
                "Comprehensive Answer:",
            ),
        ]
    )
