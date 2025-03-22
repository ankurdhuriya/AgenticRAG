from langchain_core.prompts.chat import ChatPromptTemplate


def get_grade_prompt() -> ChatPromptTemplate:
    """Get the grade prompt template."""
    system = """You are a grader assessing relevance of a retrieved document to a user question. 
        If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. 
        Give a binary score 'Yes' or 'No' score to indicate whether the document is relevant to the question."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Retrieved document: \n\n {document} \n\n User question: {question}",
            ),
        ]
    )


def get_rewrite_prompt() -> ChatPromptTemplate:
    """Get the rewrite prompt template."""
    system = """You a question re-writer that converts an input question to a better version that is optimized 
        for retrieval. Look at the input and try to reason about the underlying semantic intent / meaning."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            (
                "human",
                "Here is the initial question: \n\n {question} \n Formulate an improved question.",
            ),
        ]
    )


def get_answer_prompt() -> ChatPromptTemplate:
    """Get the answer prompt template."""
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    return ChatPromptTemplate.from_template(template=template)
