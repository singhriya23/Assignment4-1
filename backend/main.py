from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from pdf_parser import pdf_to_markdown  # Your existing pdf_to_markdown function
from gcs_utils import list_files_in_gcs, download_file_from_gcs
from io import BytesIO
import urllib.parse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI PDF Processing & Q/A Service"}

@app.get("/list_pdf_files")
def list_files_in_pdf_folder():
    """List all PDF files from the 'pdf_files' folder in GCS."""
    folder_name = "pdf_files"
    files = list_files_in_gcs(folder_name)
    return {"files": files}

@app.post("/upload_and_parse_pdf/")
async def upload_and_parse_pdf(file: UploadFile = File(...), parse_method: str = Query("pymupdf", enum=["pymupdf", "mistral", "docling"])):
    """Upload a PDF, parse it using a selected method, and convert it to Markdown."""
    try:
        if parse_method == "pymupdf":
            markdown_content = await pdf_to_markdown(file)
        elif parse_method == "mistral":
            print("awaiting code")
        elif parse_method == "docling":
            print("awaiting code")
        else:
            raise HTTPException(status_code=400, detail="Invalid parse method selected.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while parsing the PDF: {str(e)}")
    
    return {"markdown_content": markdown_content}



# Helper function to handle BytesIO and pass the original file name
async def pdf_to_markdown_from_bytes(file: BytesIO, filename: str):
    """Extracts text from a PDF-like object and returns it as markdown."""
    
    # Create a mock UploadFile from the BytesIO object
    class MockUploadFile:
        def __init__(self, file_like_object, filename):
            self.file = file_like_object
            self.filename = filename  # Pass the original filename

        async def read(self):
            return self.file.read()

    # Pass the BytesIO as a mock UploadFile object to the original pdf_to_markdown function
    mock_file = MockUploadFile(file, filename)
    return await pdf_to_markdown(mock_file)

@app.get("/parse_gcs_pdf/")
async def parse_gcs_pdf(file_name: str = Query(...), parse_method: str = Query("pymupdf", enum=["pymupdf", "mistral", "docling"])):
    """Parse a selected PDF file from GCS."""
    try:
        # Download the file content as bytes from GCS
        file_content = download_file_from_gcs(file_name)  # This returns file content as bytes
      
        if not file_content:
            raise HTTPException(status_code=404, detail="File not found in GCS")
        
        if file_name.startswith("pdf_files/"):
            file_name = file_name[len("pdf_files/"):]

        # Convert the byte content into a file-like object using BytesIO
        file_like_object = BytesIO(file_content)
        
        # Call the corresponding parsing method based on the `parse_method` parameter
        if parse_method == "pymupdf":
            markdown_content = await pdf_to_markdown_from_bytes(file_like_object, file_name)
        elif parse_method == "mistral":
            markdown_content = await pdf_to_markdown_mistral(file_like_object, file_name)
        elif parse_method == "docling":
            markdown_content = await pdf_to_markdown_docling(file_like_object, file_name)
        else:
            raise HTTPException(status_code=400, detail="Invalid parse method selected.")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while parsing the PDF: {str(e)}")
    
    return {"markdown_content": markdown_content}

