from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from Langchain_Chunking import langchain_chunking  # Import chunking function from Langchain_Chunking.py

vector_store = Chroma(
    collection_name="nvidia-reports",  # Name of the collection in ChromaDB
    embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"
),
persist_directory="./chroma_langchain_db"
  )  # Initialize ChromaDB client

pdf_path = "10K10Q-Quarter-1-2025.pdf"
chunks = langchain_chunking(pdf_path)

from langchain.schema import Document

documents = [Document(page_content=chunk) for chunk in chunks]
vector_store.add_documents(documents)

print("Successfully stored chunks in ChromaDB using Hugging Face embeddings.")

def query_chroma(query, top_k=3):
    results = vector_store.similarity_search(query, k=top_k)
    return results

query = "What was NVIDIA's revenue in Q1 2025?"
results = query_chroma(query)

print("🔍 Top Results:")
for res in results:
    print(res.page_content)
