"""
Schemas for incoming requests
"""
from pydantic import BaseModel
from typing import Optional


class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 150
    model_name: str = "llama3.2"


class TTSRequest(BaseModel):
    text: str
    title: Optional[str] = None
    voice: str = "en_US-amy-medium"
    output_format: str = "wav"
    clean_text: bool = True  # Default to True for automatic text cleaning