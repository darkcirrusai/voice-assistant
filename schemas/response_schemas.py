"""
Schemas for responses
"""
from pydantic import BaseModel


class SummarizationResponse(BaseModel):
    original_length: str
    summary: str
    summary_length: str
    status: str


class TTSResponse(BaseModel):
    status: str
    message: str
    filename: str
    format: str
