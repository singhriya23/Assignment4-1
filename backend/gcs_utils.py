from google.cloud import storage
from fastapi.responses import StreamingResponse
import io

# Set your GCS bucket name
BUCKET_NAME = "pdfstorage_1"

# Initialize the GCS client
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

def upload_to_gcs(file_stream, destination_blob_name: str, content_type: str = "text/markdown") -> str:
    """Uploads an in-memory file to Google Cloud Storage and returns the file URL."""
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file_stream, content_type=content_type)
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}"

def list_files_in_gcs():
    """Lists all files in the GCS bucket."""
    return [blob.name for blob in bucket.list_blobs()]

def get_file_content(file_name):
    """Fetches the content of a markdown file from GCS."""
    blob = bucket.blob(file_name)
    return blob.download_as_text()

def download_file_from_gcs(file_name):
    """Fetches the file from GCS and returns it as a streaming response."""
    blob = bucket.blob(file_name)
    file_data = blob.download_as_bytes()
    
    file_stream = io.BytesIO(file_data)  # Convert bytes to a stream
    
    return StreamingResponse(file_stream, media_type="application/octet-stream", 
                             headers={"Content-Disposition": f"attachment; filename={file_name}"})
