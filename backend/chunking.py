import json
import nltk
from nltk.tokenize import sent_tokenize
from google.cloud import storage
nltk.download('punkt')


# 1. Fixed-size chunking (every N words)
def chunk_fixed_size(text, chunk_size=200):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# 2. Semantic-based chunking (split at sentence boundaries)
def chunk_by_sentences(text, max_sentences=5):
    sentences = sent_tokenize(text)
    return [' '.join(sentences[i:i+max_sentences]) for i in range(0, len(sentences), max_sentences)]

# 3. Sliding window chunking (overlapping chunks)
def chunk_sliding_window(text, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(' '.join(words[i:i+chunk_size]))
    return chunks

def process_and_store_chunked_data(bucket_name, input_file_path, output_file_path):
    """Reads the chunked_text.json from GCS, processes it, and uploads the updated version to GCS."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Download the JSON file from GCS
    input_blob = bucket.blob(input_file_path)
    if not input_blob.exists():
        print(f"File {input_file_path} not found in bucket {bucket_name}.")
        return
    
    # Load data
    content = input_blob.download_as_text()
    md_files = json.loads(content)

    # Apply chunking logic
    all_chunks = {}
    for filename, text in md_files.items():
        chunks = (
            chunk_fixed_size(text) +
            chunk_by_sentences(text) +
            chunk_sliding_window(text)
        )
        all_chunks[filename] = chunks

    # Save processed data locally before uploading
    local_json_path = "/tmp/chunked_text.json"
    with open(local_json_path, "w") as f:
        json.dump(all_chunks, f)

    # Upload updated chunked data to GCS
    output_blob = bucket.blob(output_file_path)
    output_blob.upload_from_filename(local_json_path)

    print(f"Chunking completed and stored in GCS at {output_file_path}.")

if __name__ == "__main__":
    bucket_name = "pdfstorage_1"
    input_file_path = "rags/PDF_File(1).pdf.json"  # Update path if stored elsewhere
    output_file_path = "rags/chunked/chunked_text.json"

    process_and_store_chunked_data(bucket_name, input_file_path, output_file_path)
