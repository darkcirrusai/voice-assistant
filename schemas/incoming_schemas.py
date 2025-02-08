"""
Schemas for incoming requests
"""
from pydantic import BaseModel


class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 150
    model_name: str = "llama3.2"


class TTSRequest(BaseModel):
    text: str
    voice: str = "en_US-amy-medium"
    output_format: str = "mp3"
    title: str = None