import json
import numpy as np
from numpy.linalg import norm
import openai
from google.cloud import storage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path=".env")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Google Cloud Storage Configuration
BUCKET_NAME = "pdfstorage_1"
GCS_EMBEDDINGS_PATH = "rags/embeddings/embeddings.json"
LOCAL_EMBEDDINGS_PATH = "embeddings.json"  # Save in the current folder
LOCAL_RESULTS_PATH = "search_results.json"  # Save in the current folder

def download_embeddings(bucket_name, source_path, destination_path):
    """Downloads embeddings.json file from GCS."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(source_path)

    if not blob.exists():
        print(f"❌ File {source_path} not found in bucket {bucket_name}.")
        return False

    blob.download_to_filename(destination_path)
    print(f"✅ Downloaded {source_path} from GCS to {destination_path}.")
    return True

def get_embedding(text):
    """Generates embedding using OpenAI model."""
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response["data"][0]["embedding"]

def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def search(query, quarter_filter=None, top_n=5):
    """Search for relevant chunks based on cosine similarity, with optional quarter filtering."""
    
    # Ensure embeddings file is available
    if not download_embeddings(BUCKET_NAME, GCS_EMBEDDINGS_PATH, LOCAL_EMBEDDINGS_PATH):
        return []

    query_embedding = get_embedding(query)

    with open(LOCAL_EMBEDDINGS_PATH, "r") as f:
        indexed_data = json.load(f)

    # Filter by quarter if specified
    filtered_data = [item for item in indexed_data if quarter_filter is None or item["quarter"] == quarter_filter]

    # Compute similarity
    results = []
    for item in filtered_data:
        similarity = cosine_similarity(query_embedding, item["embedding"])
        results.append((similarity, item))

    # Sort & return top results
    results.sort(reverse=True, key=lambda x: x[0])
    top_results = [item for _, item in results[:top_n]]

    # Save search results in the current directory
    with open(LOCAL_RESULTS_PATH, "w") as f:
        json.dump(top_results, f, indent=4)

    print(f"📁 Search results saved to {LOCAL_RESULTS_PATH}")
    return top_results

if __name__ == "__main__":
    query = "How should evidence be analyzed in a paragraph?"
    results = search(query)

    print("\n🔍 **Top Matching Text Chunks:**\n")
    for res in results:
        print(f"- {res['text']}\n")
