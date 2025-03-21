import json
from langchain.vectorstores import Chroma
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

def index_json_file(json_path, collection_name="json-index", persist_directory="./chroma_langchain_db"):
    """
    Index a pre-chunked JSON file into ChromaDB.

    Args:
        json_path (str): Path to the JSON file containing pre-chunked data.
        collection_name (str): Name of the ChromaDB collection.
        persist_directory (str): Directory where the ChromaDB database is stored.

    Returns:
        Chroma: The indexed ChromaDB vector store.
    """

    # ✅ Validate file format
    if not json_path.endswith(".json"):
        raise ValueError(f"❌ Invalid file format: {json_path}. Only JSON files are allowed.")

    # ✅ Initialize ChromaDB
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
        persist_directory=persist_directory
    )

    # ✅ Read JSON file
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # ✅ Extract pre-chunked text
    if "chunks" not in data:
        raise ValueError("❌ Invalid JSON format: 'chunks' key not found.")

    documents = [Document(page_content=chunk["content"], metadata={"source": json_path, "id": chunk["id"]})
                 for chunk in data["chunks"]]

    # ✅ Insert pre-chunked documents into ChromaDB
    if documents:
        vector_store.add_documents(documents)
        print(f"✅ Successfully indexed {len(documents)} pre-chunked entries into ChromaDB ({collection_name}).")
    else:
        print("⚠️ No chunks were indexed. Check if the JSON file contains text.")

    return vector_store

# ✅ Example Usage
index_json_file("output-json/output-q1-2025.json")
