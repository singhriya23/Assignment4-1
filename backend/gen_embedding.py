import openai
import json
import re
from google.cloud import storage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

# Set OpenAI API key globally using the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_embedding(text):
    """Generates embedding using OpenAI model."""
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']

def process_and_store_embeddings(bucket_name, input_file_path, output_file_path):
    """Downloads chunked_text.json, generates embeddings, and uploads the result to GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Download the JSON file from GCS
    input_blob = bucket.blob(input_file_path)
    if not input_blob.exists():
        print(f"File {input_file_path} not found in bucket {bucket_name}.")
        return

    # Load data
    content = input_blob.download_as_text()
    chunked_data = json.loads(content)

    # Generate embeddings
    all_chunks = []
    for filename, chunks in chunked_data.items():
        quarter = re.search(r'Q\d_\d{4}', filename)  # Extract quarter info from filename
        quarter = quarter.group() if quarter else "Unknown"

        for chunk in chunks:
            embedding = get_embedding(chunk)
            all_chunks.append({
                "text": chunk,
                "embedding": embedding,
                "filename": filename,
                "quarter": quarter
            })

    # Save processed data locally before uploading
    local_json_path = "/tmp/embeddings.json"
    with open(local_json_path, "w") as f:
        json.dump(all_chunks, f)

    # Upload updated embeddings to GCS
    output_blob = bucket.blob(output_file_path)
    output_blob.upload_from_filename(local_json_path)

    print(f"Embeddings generated and stored in GCS at {output_file_path}.")

if __name__ == "__main__":
    bucket_name = "pdfstorage_1"
    input_file_path = "rags/chunked/chunked_text.json" 
    output_file_path = "rags/embeddings/embeddings.json"

    process_and_store_embeddings(bucket_name, input_file_path, output_file_path)
