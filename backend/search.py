import json
import numpy as np
from numpy.linalg import norm
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path=".env")
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_embedding(text):
    """Generates embedding using OpenAI model."""
    response = openai.embeddings.create(input=[text], model="text-embedding-ada-002")
    return response.data[0].embedding


def cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))


def search_from_content(content, query, quarter_filter=None, top_n=5):
    """
    Perform search on the provided content.
    - content: List of embedded chunks (in-memory)
    - query: Search query
    - quarter_filter: Filter results by quarter
    - top_n: Number of top results to return
    """
    # Filter content by quarter if specified
    filtered_data = [item for item in content if quarter_filter is None or item["quarter"] == quarter_filter]

    # Generate query embedding
    query_embedding = get_embedding(query)

    # Calculate similarity scores
    results = []
    for item in filtered_data:
        similarity = cosine_similarity(query_embedding, item["embedding"])
        results.append((similarity, item))

    # Sort results by similarity
    results.sort(reverse=True, key=lambda x: x[0])
    top_results = [item for _, item in results[:top_n]]

    return top_results


if __name__ == "__main__":
    # Load the embedded content for testing
    with open("embeddings.json", "r") as f:
        content = json.load(f)

    # Get query input from the user
    query = input("\n🔍 Enter your search query: ")

    # Optional: Ask for a quarter filter
    quarter_filter = input("📅 Enter quarter filter (or press Enter to skip): ").strip() or None

    # Perform search
    results = search_from_content(content, query, quarter_filter)

    print("\n🔍 **Top Matching Text Chunks:**\n")
    for res in results:
        print(f"- {res['text']}\n")
