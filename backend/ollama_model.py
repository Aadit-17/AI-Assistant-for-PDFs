"""Script to run Meta Llama 3.3-70B Instruct Turbo Free Model via Together AI API"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"


def generate_response(query, context):
    """Generate AI response using Together AI Chat Completions API (HTTP)."""
    if not TOGETHER_API_KEY:
        return "Error: Missing API Key. Please set TOGETHER_API_KEY in the environment variables."

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that answers based on provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ],
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1.1
    }

    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        if e.response is not None:
            print(f"Response text: {e.response.text}")
        return f"Error: Failed to get response from Together AI. {str(e)}"
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return f"Error: An unexpected error occurred. {str(e)}"
