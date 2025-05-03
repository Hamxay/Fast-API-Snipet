from pydantic import BaseModel


class TextData(BaseModel):
    id: str
    text: str

# Pydantic Model for the Query Result
class QueryResult(BaseModel):
    id: str
    score: float
    text: str