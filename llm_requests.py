import requests
from typing import Optional
import os
# from openai import OpenAI
# import google.generativeai as genai

def ollama_request(
    prompt: str,
    model: str = "llama3.2",
    system: str = "You are a helpful AI assistant focused on summarization.",
    temperature: float = 0.7
) -> Optional[str]:
    """
    Send a request to Ollama API
    
    Args:
        prompt: The text prompt to send
        model: The model to use (default: llama3.2)
        system: System prompt to guide the model
        temperature: Randomness in response (0-1)
    
    Returns:
        str: The model's response or None if request fails
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "temperature": temperature
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except Exception as e:
        print(f"Error in Ollama request: {e}")
        return None


if __name__ == "__main__":
    # Test the Ollama request function
    prompt = """Please summarize the following text in no more than 100 characters:

    The quick brown fox jumps over the lazy dog."""
    summary = ollama_request(
        prompt=prompt,
        system="You are a helpful AI assistant focused on creating concise and accurate summaries. Keep your summaries within the specified character limit.",
        temperature=0.3
    )
    print(summary)
