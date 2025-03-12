from fastapi import FastAPI, File, UploadFile, Body
from urllib.parse import unquote
from pdf_parser import pdf_to_markdown
from gcs_utils import list_files_in_gcs, get_file_content, download_file_from_gcs
import os
import requests
from dotenv import load_dotenv

app = FastAPI()

# Load API Key for Claude (Anthropic)
load_dotenv(dotenv_path="/Users/kaushikj/Desktop/Assignment4-1/backend/.env")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("Claude API key not set. Please set CLAUDE_API_KEY as an environment variable.")

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"  # Correct Anthropic API endpoint

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI PDF to Markdown Converter"}

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Handles PDF uploads, converts them to Markdown, and uploads to GCS."""
    markdown_info = await pdf_to_markdown(file)
    return {"message": "File processed successfully", "gcs_url": markdown_info["gcs_url"]}

@app.get("/list_files/")
def list_files():
    """Lists all files in the GCS bucket."""
    return {"files": list_files_in_gcs()}

@app.get("/get_file/{file_name:path}")
def get_file(file_name: str):
    """Fetches the Markdown file content from GCS and automatically summarizes it using Claude."""
    decoded_file_name = unquote(file_name)
    try:
        content = get_file_content(decoded_file_name)
        if not content:
            return {"error": "File content is empty"}

        # Automatically summarize the fetched content using Claude
        summary_response = summarize_file(content)

        return {
            "file_name": decoded_file_name,
            "content": content,
            "summary": summary_response["summary"]
        }
    
    except Exception as e:
        return {"error": f"Failed to fetch and summarize file: {str(e)}"}

@app.get("/download_file/{file_name:path}")
def download_file(file_name: str):
    """Provides a file for download from Google Cloud Storage."""
    decoded_file_name = unquote(file_name)
    return download_file_from_gcs(decoded_file_name)

@app.post("/summarize_file/")
def summarize_file(content: str = Body(..., embed=True)):
    """Takes the markdown content from the frontend and returns its summarized text using Claude."""
    try:
        if not content.strip():
            return {"error": "File content is empty"}

        # Summarize the content using Claude API (Direct Call)
        summary = summarize_text_claude(content)
        return {"summary": summary}
    
    except Exception as e:
        return {"error": f"Failed to summarize file: {str(e)}"}

# 🔹 Direct Claude API Call Function
def summarize_text_claude(text: str) -> str:
    """Calls Claude API directly to summarize text."""
    try:
        headers = {
            "x-api-key": CLAUDE_API_KEY,  # Claude API Key
            "anthropic-version": "2023-06-01",  # Required version
            "content-type": "application/json"
        }
        payload = {
            "model": "claude-3-opus-20240229",  # Specify the Claude model
            "max_tokens": 300,  # Limit the response length
            "messages": [
                {"role": "user", "content": f"Summarize this:\n\n{text}"}
            ],
            "temperature": 0.7  # Adjust for randomness
        }
        
        response = requests.post(CLAUDE_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()["content"]
        else:
            return f"Claude API Error: {response.json()}"
    
    except Exception as e:
        return f"Claude Summarization Failed: {str(e)}"
