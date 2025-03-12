from fastapi import FastAPI, File, UploadFile, Body
from urllib.parse import unquote
from pdf_parser import pdf_to_markdown
from gcs_utils import list_files_in_gcs, get_file_content, download_file_from_gcs
import os
import requests
from dotenv import load_dotenv

app = FastAPI()

# Load API Key for DeepSeek
load_dotenv(dotenv_path="/Users/kaushikj/Desktop/Assignment4-1/backend/.env")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DeepSeek API key not set. Please set DEEPSEEK_API_KEY as an environment variable.")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # Correct DeepSeek API endpoint

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
    """Fetches the Markdown file content from GCS and automatically summarizes it using DeepSeek."""
    decoded_file_name = unquote(file_name)
    try:
        content = get_file_content(decoded_file_name)
        if not content:
            return {"error": "File content is empty"}

        # Automatically summarize the fetched content using DeepSeek
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
    """Takes the markdown content from the frontend and returns its summarized text using DeepSeek."""
    try:
        if not content.strip():
            return {"error": "File content is empty"}

        # Summarize the content using DeepSeek API (Direct Call)
        summary = summarize_text_deepseek(content)
        return {"summary": summary}
    
    except Exception as e:
        return {"error": f"Failed to summarize file: {str(e)}"}

# 🔹 Direct DeepSeek API Call Function
def summarize_text_deepseek(text: str) -> str:
    """Calls DeepSeek API directly to summarize text."""
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": f"Summarize this:\n\n{text}"}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"DeepSeek API Error: {response.json()}"
    
    except Exception as e:
        return f"DeepSeek Summarization Failed: {str(e)}"
