
from pydantic import BaseModel
from typing import List, Optional, Any

class SQLRequest(BaseModel):
    sql: str

class SQLResponse(BaseModel):
    result: List[dict]
    rows_affected: Optional[int] = None

class RAGRequest(BaseModel):
    query: str
    k: Optional[int] = 4

class RAGResponse(BaseModel):
    answer: str
    sources: List[str]
