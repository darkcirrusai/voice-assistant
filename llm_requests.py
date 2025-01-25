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

# def openai_request(
#     prompt: str,
#     model: str = "gpt-3.5-turbo",
#     system: str = "You are a helpful AI assistant focused on summarization.",
#     temperature: float = 0.7
# ) -> Optional[str]:
#     """
#     Send a request to OpenAI API
    
#     Args:
#         prompt: The text prompt to send
#         model: The model to use
#         system: System prompt to guide the model
#         temperature: Randomness in response (0-1)
    
#     Returns:
#         str: The model's response or None if request fails
#     """
#     try:
#         client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": system},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=temperature
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"Error in OpenAI request: {e}")
#         return None

# def google_ai_request(
#     prompt: str,
#     model: str = "gemini-pro",
#     temperature: float = 0.7
# ) -> Optional[str]:
#     """
#     Send a request to Google AI API
    
#     Args:
#         prompt: The text prompt to send
#         model: The model to use
#         temperature: Randomness in response (0-1)
    
#     Returns:
#         str: The model's response or None if request fails
#     """
#     try:
#         genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
#         model = genai.GenerativeModel(model)
#         response = model.generate_content(
#             prompt,
#             generation_config=genai.types.GenerationConfig(
#                 temperature=temperature
#             )
#         )
#         return response.text
#     except Exception as e:
#         print(f"Error in Google AI request: {e}")
#         return None 