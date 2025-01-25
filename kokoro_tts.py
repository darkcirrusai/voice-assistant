import os
import subprocess
import torch
import sounddevice as sd
from kokoro.models import build_model
from kokoro.kokoro import generate

def install_dependencies():
    """Install required system dependencies"""
    # Check if running on macOS
    if os.uname().sysname == 'Darwin':
        # Install espeak-ng using Homebrew
        try:
            subprocess.run(['brew', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            print("Homebrew is not installed. Please install it first from https://brew.sh")
            raise
        
        subprocess.run(['brew', 'install', 'espeak'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    else:
        # Install espeak-ng on Linux
        subprocess.run(['apt-get', '-qq', '-y', 'install', 'espeak-ng'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)

def setup_model():
    """Setup and return the TTS model and voice"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Update path to point directly to model file in kokoro folder
    model = build_model('kokoro/kokoro-v0_19.pth', device)
    
    # Default voice is a 50-50 mix of Bella & Sarah
    voice_name = 'af'  
    # Update path to point directly to voices folder
    voicepack = torch.load(f'kokoro/voices/{voice_name}.pt', weights_only=True).to(device)
    print(f'Loaded voice: {voice_name}')
    
    return model, voicepack, voice_name

def text_to_speech(text, model, voicepack, voice_name):
    """Convert text to speech and play audio"""
    # Generate audio (24khz) and phonemes
    audio, phonemes = generate(model, text, voicepack, lang=voice_name[0])
    
    # Play audio using sounddevice
    sd.play(audio, samplerate=24000)
    sd.wait()  # Wait until audio is finished playing
    
    return phonemes

def main():
    # Setup model and voice
    model, voicepack, voice_name = setup_model()
    
    # Example text
    text = ("How could I know? It's an unanswerable question. "
            "Like asking an unborn child if they'll lead a good life. "
            "They haven't even been born.")
    
    # Generate and play speech
    phonemes = text_to_speech(text, model, voicepack, voice_name)
    print("Generated phonemes:", phonemes)

if __name__ == "__main__":
    main()
