import os
import json
from pinecone import Pinecone, ServerlessSpec
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=".env")

def index_json_content(json_content, index_name="json-index", pinecone_api_key=None, region="us-east-1"):
    """
    Index JSON content (as a string or dict) into Pinecone after chunking.

    Args:
        json_content (str or dict): The JSON content as a string or dict.
        index_name (str): Pinecone index name (lowercase, alphanumeric, dash-separated).
        pinecone_api_key (str, optional): Pinecone API key (default: from .env).
        region (str, optional): Pinecone region (default: us-east-1).
    """
    index_name = index_name.lower().replace("_", "-")

    if pinecone_api_key is None:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("❌ Pinecone API Key is missing! Please set it in the .env or pass it.")

    # Initialize Pinecone client
    pc = Pinecone(api_key=pinecone_api_key)

    # Create index if it doesn't exist
    existing_indexes = [index["name"] for index in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"⚠️ Index '{index_name}' not found. Creating it now...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=region)
        )

    index = pc.Index(index_name)

    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = PineconeVectorStore(index=index, embedding=embeddings, text_key="page_content")

    # Parse JSON
    try:
        data = json.loads(json_content) if isinstance(json_content, str) else json_content
    except json.JSONDecodeError:
        raise ValueError("❌ Failed to parse JSON string.")

    if 'chunks' not in data or not isinstance(data['chunks'], list):
        raise ValueError("❌ No valid 'chunks' found in JSON content.")

    chunks = [
        chunk.get("content", "") if isinstance(chunk, dict) else chunk
        for chunk in data["chunks"]
    ]

    documents = [
        Document(page_content=chunk, metadata={"source": "in-memory"})
        for chunk in chunks if chunk
    ]

    if documents:
        vector_store.add_documents(documents)
        print(f"✅ Successfully indexed {len(documents)} chunks into Pinecone ({index_name}).")
    else:
        print("⚠️ No chunks were created. JSON content might be empty.")

    return vector_store
