"""
Schemas for responses
"""
from pydantic import BaseModel


class SummarizationResponse(BaseModel):
    original_length: int
    summary: str
    summary_length: int
    status: str


class TTSResponse(BaseModel):
    status: str
    message: str
    filename: str
    format: str
