from fastapi import FastAPI, File, UploadFile, Body
from urllib.parse import unquote
from pdf_parser import pdf_to_markdown
from gcs_utils import list_files_in_gcs, get_file_content, download_file_from_gcs
from summarization_gpt import summarize_text_gpt
from summarization_gemini import summarize_text_gemini


app = FastAPI()

# Model mapping dictionary
SUMMARIZATION_MODELS = {
    "gpt": summarize_text_gpt,
    "gemini": summarize_text_gemini 
}

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
    """Fetches the Markdown file content from GCS and automatically summarizes it."""
    decoded_file_name = unquote(file_name)
    try:
        content = get_file_content(decoded_file_name)
        if not content:
            return {"error": "File content is empty"}

        # Automatically summarize the fetched content using the default model (GPT)
        summary_response = summarize_file(content=content, model="gpt")

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
def summarize_file(content: str = Body(..., embed=True), model: str = Body("gpt", embed=True)):
    """Summarizes the given text using the selected model."""
    try:
        if not content.strip():
            return {"error": "File content is empty"}
        
        if model not in SUMMARIZATION_MODELS:
            return {"error": f"Invalid model '{model}'. Choose from {list(SUMMARIZATION_MODELS.keys())}"}
        
        # Call the appropriate summarization function
        summarization_function = SUMMARIZATION_MODELS[model]
        summary = summarization_function(content)

        return {"summary": summary}
    
    except Exception as e:
        return {"error": f"Failed to summarize file: {str(e)}"}
