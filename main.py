from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import tempfile
import os
from piper_tts import piper_tts
from llm_requests import ollama_request

app = FastAPI(
    title="Audio Processing and Summarization API",
    description="API for audio conversion and text summarization",
    version="1.0.0"
)

class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 150

class TTSRequest(BaseModel):
    text: str
    voice: str = "en_US-amy-medium"
    output_format: str = "mp3"

@app.get("/")
async def get_info():
    """Return basic information about the API"""
    return {
        "name": "Audio Processing and Summarization API",
        "version": "1.0.0",
        "endpoints": [
            "/",
            "/convert-audio",
            "/summarize"
        ]
    }

@app.post("/convert-audio")
async def convert_audio(text_data: TTSRequest,
                        title: str = None):
    """
    Convert text to speech using Piper TTS
    """
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create input text file
            input_file = os.path.join(temp_dir, f"{title}.txt")
            with open(input_file, "w") as f:
                f.write(text_data.text)
            
            # Create output filename
            output_file = os.path.join(temp_dir, f"{title}.{text_data.output_format}")
            
            # Process TTS conversion
            result = piper_tts(
                input_file=input_file,
                voice=text_data.voice,
                output=output_file
            )
            
            if not result:
                raise HTTPException(status_code=500, detail="TTS conversion failed")
            
            # Read the audio file
            with open(output_file, "rb") as audio_file:
                audio_content = audio_file.read()
            
            return {
                "status": "success",
                "message": "Audio conversion completed",
                "audio_data": audio_content,
                "format": text_data.output_format
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize_text(request: SummarizationRequest):
    """
    Summarize provided text using Ollama
    """
    try:
        prompt = f"""Please summarize the following text in no more than {request.max_length} characters:

{request.text}"""

        summary = ollama_request(
            prompt=prompt,
            system="You are a helpful AI assistant focused on creating concise and accurate summaries. Keep your summaries within the specified character limit.",
            temperature=0.3
        )
        
        if not summary:
            raise HTTPException(status_code=500, detail="Summarization failed")
            
        return {
            "original_length": len(request.text),
            "summary": summary,
            "summary_length": len(summary),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9050, reload=True) 