import os
import json
import nltk
from nltk.tokenize import sent_tokenize
from io import BytesIO  # Changed from StringIO to BytesIO
from gcs_utils import upload_to_gcs  # Import the upload function

nltk.download('punkt')

# 1. Fixed-size chunking (every N words)
def chunk_fixed_size(text, chunk_size=200):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]


# 2. Semantic-based chunking (split at sentence boundaries)
def chunk_by_sentences(text, max_sentences=5):
    sentences = sent_tokenize(text)
    return [' '.join(sentences[i:i + max_sentences]) for i in range(0, len(sentences), max_sentences)]


# 3. Sliding window chunking (overlapping chunks)
def chunk_sliding_window(text, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(' '.join(words[i:i + chunk_size]))
    return chunks


def process_and_upload_chunked_data(text, destination_blob_name, strategy):
    """Process text with the selected chunking strategy and upload chunked data to GCS."""
    
    # Apply the selected chunking strategy
    if strategy == "fixed":
        chunked_data = chunk_fixed_size(text)
    elif strategy == "sentence":
        chunked_data = chunk_by_sentences(text)
    elif strategy == "sliding":
        chunked_data = chunk_sliding_window(text)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Prepare output as JSON structure
    chunked_json = {"chunks": chunked_data}

    destination_blob_name = os.path.splitext(destination_blob_name)[0] + ".json"

    # Convert the chunked data to a JSON string
    chunked_json_str = json.dumps(chunked_json, ensure_ascii=False, indent=4)

    # Convert the string to bytes
    file_stream = BytesIO(chunked_json_str.encode('utf-8'))  # Encode the string to bytes

    # Upload the chunked data to GCS
    try:
        file_url = upload_to_gcs(file_stream, destination_blob_name, content_type="application/json")
        print(f"File uploaded successfully to GCS: {file_url}")
        return file_url
    except Exception as e:
        print(f"Error uploading to GCS: {e}")
        raise ValueError(f"Error uploading to GCS: {e}")
