import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Define Claude API endpoint
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

def summarize_text_claude(text):
    """Use Claude (Anthropic) to summarize extracted text from a PDF."""
    print("claude called")
    headers = {
        "x-api-key": CLAUDE_API_KEY,  # Claude API Key
        "anthropic-version": "2023-06-01",  # Required API version
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-opus-2024-02-29",  # Specify the Claude model
        "max_tokens": 300,  # Limit the response length
        "messages": [
            {"role": "system", "content": "You are an AI that summarizes documents concisely."},
            {"role": "user", "content": f"Summarize the following document:\n\n{text}"}
        ],
        "temperature": 0.7  # Adjust for randomness
    }

    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()["content"]
        else:
            return f"Claude API Error: {response.json()}"
    
    except Exception as e:
        return f"Claude Summarization Failed: {str(e)}"
