from pathlib import Path
from piper_tts import piper_tts

def process_text_file(
    input_file: str | Path,
    output_file: str | Path,
    voice: str = "en_US-amy-medium"
) -> bool:
    """
    Process a text file directly using Piper TTS
    
    Args:
        input_file: Path to input text file
        output_file: Path to output audio file
        voice: Voice model to use
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        result = piper_tts(
            input_file=str(input_file),
            voice=voice,
            output=str(output_file)
        )
        return result is not None
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    success = process_text_file(
        input_file="input.txt",
        output_file="output.mp3",
        voice="en_US-amy-medium"
    )
    print(f"Processing {'successful' if success else 'failed'}") 