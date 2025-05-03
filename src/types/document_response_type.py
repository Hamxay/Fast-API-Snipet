from pydantic import BaseModel
from typing import List


class SourceDocument(BaseModel):
    filename: str
    download_url: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]


class UploadResponse(BaseModel):
    message: str


class DownloadDocumentResponse(BaseModel):
    download_url: str
