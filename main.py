from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import uvicorn
import tempfile
import os
from datetime import datetime
from piper_tts import piper_tts
from llm_requests import ollama_request
from starlette.requests import Request

# Create static directory if it doesn't exist
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI(
    title="Audio Processing and Summarization API",
    description="API for audio conversion and text summarization",
    version="1.0.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

class SummarizationRequest(BaseModel):
    text: str
    max_length: int = 150

class TTSRequest(BaseModel):
    text: str
    voice: str = "en_US-amy-medium"
    output_format: str = "mp3"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with list of audio files and API info"""
    # Get audio files
    audio_files = []
    for filename in os.listdir(AUDIO_DIR):
        filepath = os.path.join(AUDIO_DIR, filename)
        created = datetime.fromtimestamp(os.path.getctime(filepath))
        title, format = os.path.splitext(filename)
        format = format.lstrip('.')
        audio_files.append({
            "filename": filename,
            "title": title,
            "format": format,
            "created": created.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Sort files by creation date, newest first
    audio_files.sort(key=lambda x: x["created"], reverse=True)
    
    # API information
    api_info = {
        "name": "Audio Processing and Summarization API",
        "version": "1.0.0",
        "endpoints": [
            "/",
            "/convert-audio",
            "/summarize"
        ]
    }
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request, 
            "audio_files": audio_files,
            "api_info": api_info
        }
    )

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve audio files"""
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)

@app.post("/convert-audio")
async def convert_audio(text_data: TTSRequest, title: str = None):
    """
    Convert text to speech using Piper TTS and save to static directory
    """
    try:
        # Generate a filename if title is not provided
        if not title:
            title = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create input text file
            input_file = os.path.join(temp_dir, f"{title}.txt")
            with open(input_file, "w") as f:
                f.write(text_data.text)
            
            # Create output filename in temp directory
            temp_output = os.path.join(temp_dir, f"{title}.{text_data.output_format}")
            
            # Process TTS conversion
            result = piper_tts(
                input_file=input_file,
                voice=text_data.voice,
                output=temp_output
            )
            
            if not result:
                raise HTTPException(status_code=500, detail="TTS conversion failed")
            
            # Move the file to the static directory
            final_output = os.path.join(AUDIO_DIR, f"{title}.{text_data.output_format}")
            with open(temp_output, "rb") as src, open(final_output, "wb") as dst:
                dst.write(src.read())
            
            return {
                "status": "success",
                "message": "Audio conversion completed",
                "filename": f"{title}.{text_data.output_format}",
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