from fastapi import FastAPI, File, UploadFile
from urllib.parse import unquote
from pdf_parser import pdf_to_markdown
from gcs_utils import list_files_in_gcs, get_file_content, download_file_from_gcs

app = FastAPI()

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
    """Fetches and returns the contents of a selected Markdown file."""
    decoded_file_name = unquote(file_name)
    try:
        content = get_file_content(decoded_file_name)
        return {"file_name": decoded_file_name, "content": content}
    except Exception as e:
        return {"error": f"Failed to fetch file: {str(e)}"}

@app.get("/download_file/{file_name:path}")
def download_file(file_name: str):
    """Provides a file for download from Google Cloud Storage."""
    decoded_file_name = unquote(file_name)
    return download_file_from_gcs(decoded_file_name)
