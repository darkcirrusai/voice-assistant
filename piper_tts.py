"""
use sub process to run a piper tts conversion command
"""
import subprocess
import shlex
import time
from tqdm import tqdm
from pydub import AudioSegment


def piper_tts(input_file,voice,output):
    """
    Use piper tts to convert text from a file to speech with a progress bar
    """
    # Create a temporary WAV filename
    temp_wav = output.rsplit('.', 1)[0] + '_temp.wav'
    
    cmd = f"piper --model {voice} --output_file {temp_wav}"

    try:
        with open(input_file,'r') as f:
            input_text = f.read()

        # Use Popen to create a pipe for stdin
        process = subprocess.Popen(
            shlex.split(cmd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Create a progress bar
        with tqdm(total=100,desc="Processing",bar_format='{l_bar}{bar}',ncols=50) as pbar:
            # Send the input text to stdin and wait for it to be processed
            _, stderr = process.communicate(input=input_text)
            
            # Ensure the progress bar reaches 100%
            pbar.n = 100
            pbar.refresh()

        if process.returncode != 0:
            print(f"Error occurred: {stderr}")
            return None

        # Convert WAV to MP3 if output is MP3
        if output.lower().endswith('.mp3'):
            audio = AudioSegment.from_wav(temp_wav)
            audio.export(output, format='mp3')
            # Remove temporary WAV file
            subprocess.run(['rm', temp_wav])
            print(f"Converted to MP3. Output saved to {output}")
        else:
            # If not MP3, just rename the temp file to the desired output name
            subprocess.run(['mv', temp_wav, output])
            print(f"TTS conversion completed. Output saved to {output}")
            
        return output

    except FileNotFoundError:
        print(f"Input file not found: {input_file}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error occurred: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    test_input_file = "input.txt"
    piper_tts(input_file=test_input_file,
              voice="en_US-amy-medium",
              output="output.wav")
