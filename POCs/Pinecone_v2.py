import os
import json
from pinecone import Pinecone, ServerlessSpec  
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv  # Load environment variables

# ✅ Load .env file
load_dotenv(dotenv_path="POCs/.env")

def index_json_file(json_path, index_name="json-index", pinecone_api_key=None, region="us-east-1"):
    """
    Index a JSON file into Pinecone after chunking.

    Args:
        json_path (str): Path to the JSON file.
        index_name (str): Name of the Pinecone index (must be lowercase, alphanumeric, and use '-' instead of '_').
        pinecone_api_key (str, optional): Pinecone API key (defaults to environment variable).
        region (str, optional): Pinecone region (default: us-east-1).

    Returns:
        PineconeVectorStore: The indexed Pinecone vector store.
    """

    # ✅ Ensure index name follows Pinecone rules
    index_name = index_name.lower().replace("_", "-")  # Convert to lowercase & replace underscores

    # ✅ Load Pinecone API Key
    if pinecone_api_key is None:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("❌ Pinecone API Key is missing! Set it in the environment or pass it as an argument.")

    # ✅ Initialize Pinecone Client
    pc = Pinecone(api_key=pinecone_api_key)

    # ✅ Retrieve list of existing indexes
    existing_indexes = [index["name"] for index in pc.list_indexes()]

    # ✅ If the index does not exist, create it
    if index_name not in existing_indexes:
        print(f"⚠️ Index '{index_name}' not found. Creating it now...")

        pc.create_index(
            name=index_name,  
            dimension=384,  # Ensure dimension matches the embedding model
            metric="cosine",  
            spec=ServerlessSpec(cloud="aws", region=region)  
        )

    # ✅ Retrieve the correct Pinecone Index object
    index = pc.Index(index_name)

    # ✅ Load Embeddings
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    # ✅ Initialize the Vector Store
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        text_key="page_content",
    )

    # ✅ Read JSON file
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # ✅ Extract text chunks from JSON
    chunks = [chunk["content"] for chunk in data.get("chunks", [])]  # Extract 'content' from each chunk

    # ✅ Convert chunks to LangChain Documents
    documents = [Document(page_content=chunk, metadata={"source": json_path}) for chunk in chunks]

    # ✅ Insert chunks into Pinecone
    if documents:
        vector_store.add_documents(documents)
        print(f"✅ Successfully indexed {len(documents)} chunks into Pinecone ({index_name}).")
    else:
        print("⚠️ No chunks were created. Check if the JSON file contains text.")

    return vector_store

# ✅ Example Usage
index_json_file("output-json/output-q1-2025.json", index_name="json-index")  # Ensure index name follows rules
