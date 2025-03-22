from pydantic import BaseModel, StrictStr
from typing import List

class QuestionRequest(BaseModel):
    questions: List[StrictStr]

class QuestionAnswer(BaseModel):
    question: StrictStr
    answer: StrictStr

class AnswerResponse(BaseModel):
    answers : List[QuestionAnswer]