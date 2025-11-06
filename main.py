from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import tempfile
import os
from datetime import datetime
from piper_tts import piper_tts
from llm_requests import ollama_request
from fastapi.requests import Request
from schemas.response_schemas import SummarizationResponse, TTSResponse
from schemas.incoming_schemas import SummarizationRequest, TTSRequest

# Create static directory if it doesn't exist
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI(
    title="Audio Processing and Summarization API",
    description="API for audio conversion and text summarization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware, # noqa
    allow_origins=["*",
                   "chrome-extension://*"],  # Allow your extension to access
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS and POST
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    return FileResponse("static/favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with list of audio files and API info"""
    # Get audio files
    audio_files = []
    for filename in os.listdir(AUDIO_DIR):
        filepath = os.path.join(AUDIO_DIR, filename)
        created = datetime.fromtimestamp(os.path.getctime(filepath))
        title, audio_format = os.path.splitext(filename)
        audio_format = audio_format.lstrip('.')
        audio_files.append({
            "filename": filename,
            "title": title,
            "format": audio_format,
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


@app.post("/convert-audio",
          response_model=TTSResponse)
async def convert_audio(text_data: TTSRequest):
    """
    Convert text to speech using Piper TTS and save to static directory
    """
    try:
        # Generate a filename if title is not provided
        if not text_data.title:
            title = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            # Replace spaces with underscores in the title
            title = text_data.title.replace(" ", "_")
        
        # Clean the text using LLM if clean_text flag is set (default is True)
        text_to_process = text_data.text
        if text_data.clean_text:
            try:
                cleaning_prompt = """Please clean the following text by:
                1. Removing any headers, footers, and marketing material
                2. Removing navigation elements and hyperlink texts
                3. Eliminating any redundant or non-essential content
                4. Preserving the main content and meaning
                5. Maintaining paragraph structure of the main content

                Return ONLY the cleaned text, with no additional commentary or explanation.

                Here's the text to clean:

                """
                cleaned_text = ollama_request(
                    prompt=cleaning_prompt + text_data.text,
                    system="You are a helpful assistant that specializes in cleaning up web content for better readability and audio conversion.",
                    temperature=0.1
                )
                if cleaned_text:
                    text_to_process = cleaned_text
            except Exception as clean_error:
                # If cleaning fails, log it but continue with original text
                print(f"Text cleaning failed: {clean_error}. Proceeding with original text.")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create input text file with better error handling
            input_file = os.path.join(temp_dir, f"{title}.txt")
            try:
                with open(input_file, "w", encoding="utf-8") as f:
                    f.write(text_to_process)
            except Exception as text_error:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error processing text: {str(text_error)}. Text may contain invalid characters."
                )
            
            # Create output filename in temp directory
            temp_output = os.path.join(temp_dir, f"{title}.{text_data.output_format}")
            
            # Process TTS conversion
            try:
                result = piper_tts(
                    input_file=input_file,
                    voice=text_data.voice,
                    output=temp_output
                )
            except Exception as tts_error:
                raise HTTPException(
                    status_code=500, 
                    detail=f"TTS conversion failed: {str(tts_error)}"
                )
            
            if not result:
                raise HTTPException(status_code=500, detail="TTS conversion failed")
            
            # Move the file to the static directory
            final_output = os.path.join(AUDIO_DIR, f"{title}.{text_data.output_format}")
            try:
                with open(temp_output, "rb") as src, open(final_output, "wb") as dst:
                    dst.write(src.read())
            except Exception as file_error:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error saving audio file: {str(file_error)}"
                )
            
            return {
                "status": "success",
                "message": "Audio conversion completed",
                "filename": f"{title}.{text_data.output_format}",
                "format": text_data.output_format
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/summarize",
          response_model=SummarizationResponse)
async def summarize_text(request: SummarizationRequest):
    """
    Summarize provided text using Ollama
    """
    try:
        prompt = f"""Please summarize the following text in no more than {request.max_length} characters:

{request.text}"""

        summary = ollama_request(
            model="deepseek-r1:1.5b",
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


@app.delete("/audio/{filename}")
async def delete_audio(filename: str):
    """Delete an audio file"""
    file_path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    try:
        os.remove(file_path)
        return {"status": "success", "message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9050, reload=True) 