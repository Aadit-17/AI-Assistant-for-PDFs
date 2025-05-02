"""Script to run Meta Llama Vision Free Model via Together AI API"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variables
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"


def generate_response(query, context):
    """Generate AI response using Together AI API."""
    if not TOGETHER_API_KEY:
        return "Error: Missing API Key. Please set TOGETHER_API_KEY in the environment variables."

    prompt = f"Given the following context:\n\n{context}\n\nAnswer the question: {query}"

    try:
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "meta-llama/Llama-2-70b-chat-hf",
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "stop": ["</s>", "Human:", "Assistant:"]
        }

        response = requests.post(TOGETHER_API_URL, headers=headers, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes

        result = response.json()
        return result['choices'][0]['text']
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response text: {e.response.text}")
        return f"Error: Failed to get response from AI model. {str(e)}"
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: An unexpected error occurred. {str(e)}"
