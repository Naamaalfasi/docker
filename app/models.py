from pydantic import BaseModel, Field
from typing import List

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question about the papers")


class Citation(BaseModel):
    document_name: str
    chunk_id: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]

