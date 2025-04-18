"""Script to run Meta Llama Vision Free Model via Together AI API"""
import os
import together
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variables
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


def get_together_client():
    """Get or create a Together client instance."""
    if not TOGETHER_API_KEY:
        raise ValueError("TOGETHER_API_KEY environment variable is not set")
    together.api_key = TOGETHER_API_KEY
    return together


def generate_response(query, context):
    """Generate AI response using Meta Llama Vision Free API from Together AI."""
    if not TOGETHER_API_KEY:
        return "Error: Missing API Key. Please set TOGETHER_API_KEY in the environment variables."

    prompt = f"Given the following context:\n\n{context}\n\nAnswer the question: {query}"

    try:
        client = get_together_client()
        response = client.Complete.create(
            prompt=prompt,
            model="meta-llama/Llama-2-70b-chat-hf",
            max_tokens=512,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1.1
        )
        return response['output']['choices'][0]['text']
    except Exception as e:
        return f"Error: {e}"
