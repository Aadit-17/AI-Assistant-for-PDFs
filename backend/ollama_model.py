"""Script to run Meta Llama Vision Free Model via Together AI API"""
import os
from together import Together
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variables
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


def get_together_client():
    """Get or create a Together client instance."""
    if not TOGETHER_API_KEY:
        raise ValueError("TOGETHER_API_KEY environment variable is not set")
    return Together(api_key=TOGETHER_API_KEY)


def generate_response(query, context):
    """Generate AI response using Meta Llama Vision Free API from Together AI."""
    if not TOGETHER_API_KEY:
        return "Error: Missing API Key. Please set TOGETHER_API_KEY in the environment variables."

    prompt = f"Given the following context:\n\n{context}\n\nAnswer the question: {query}"

    try:
        client = get_together_client()
        response = client.chat.completions.create(
            model="meta-llama/Llama-Vision-Free",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"
