"""Script to run Meta Llama 3.3-70B Instruct Turbo via Together AI SDK"""
import os
from dotenv import load_dotenv
from together import Together

# Load environment variables from .env file
load_dotenv()

# Initialize Together client
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)

# Updated model name
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"


def generate_response(query, context):
    """Generate AI response using Together AI SDK (chat API)."""
    if not TOGETHER_API_KEY:
        return "Error: Missing API Key. Please set TOGETHER_API_KEY in the environment variables."

    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: An unexpected error occurred. {str(e)}"
