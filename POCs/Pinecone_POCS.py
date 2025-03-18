import os
from pinecone import Pinecone, ServerlessSpec
from langchain.vectorstores import Pinecone as PineconeVectorStore
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from Langchain_Chunking import langchain_chunking 
 # Import chunking function from langchain_file.py

# 1️⃣ Load environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # Set your Pinecone API key
PINECONE_ENV = "us-east1"  # Adjust based on your region


pc = Pinecone(api_key=PINECONE_API_KEY)

# Define the index name
INDEX_NAME = "nvidia-reports"


if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # Hugging Face MiniLM has 384 dimensions
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),  # Adjust the region if needed
    )


index = pc.Index(INDEX_NAME)

# 5️⃣ Load and Chunk the PDF
pdf_path = "10K10Q-Quarter-1-2025.pdf"
chunks = langchain_chunking(pdf_path)

# 6️⃣ Use Hugging Face Embeddings
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"  # A lightweight & efficient model
embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

# 7️⃣ Create a Pinecone Vector Store instance
vector_store = PineconeVectorStore(index, embeddings, "text")

# 8️⃣ Insert Chunks into Pinecone
from langchain.schema import Document

documents = [Document(page_content=chunk) for chunk in chunks]
vector_store.add_documents(documents)

print(f"✅ Successfully stored {len(chunks)} chunks in Pinecone using Hugging Face embeddings.")

# 9️⃣ Querying the Pinecone Vector Database
def query_pinecone(query, top_k=3):
    results = vector_store.similarity_search(query, k=top_k)
    return results

# Example Query
query = "What was NVIDIA's revenue in Q1 2022?"
results = query_pinecone(query)

print("🔍 Top Results:")
for res in results:
    print(res.page_content)
