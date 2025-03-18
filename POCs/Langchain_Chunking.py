from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def langchain_chunking(pdf_path, chunk_size=512, chunk_overlap=50):
    """
    Reads a PDF and chunks the text using LangChain's RecursiveCharacterTextSplitter.
    
    Args:
        pdf_path (str): Path to the PDF file.
        chunk_size (int): The size of each chunk (default: 512).
        chunk_overlap (int): Overlapping tokens between chunks (default: 50).
    
    Returns:
        list: A list of text chunks.
    """
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(pages)

    return [chunk.page_content for chunk in chunks]

# Example Usage
chunks = langchain_chunking("10K10Q-Quarter-1-2025.pdf", chunk_size=512, chunk_overlap=50)
print(chunks[:3])  # Preview first 3 chunks
