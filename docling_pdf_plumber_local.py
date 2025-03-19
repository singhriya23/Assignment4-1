import os
import pdfplumber
from convert_pdf_markdown import Document  # Import docling's Document class
from pathlib import Path

# Hardcoded input and output directories
input_dir = "/Users/kaushikj/Desktop/Assignment4-2/NVIDIA-PDFs"  # Replace with the full path to your input folder
output_dir = "/Users/kaushikj/Desktop/Assignment4-2/DOCLING_PDF_PLUMBER_Markdowns"  # Replace with the full path to your output folder

# Create the output directory if it doesn't exist
Path(output_dir).mkdir(parents=True, exist_ok=True)

# Function to extract text from a PDF using pdfplumber
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to convert text to Markdown using docling
def text_to_markdown(text):
    # Create a docling Document object
    doc = Document(text)
    # Convert the document to Markdown
    markdown = doc.to_markdown()  # Assuming docling has a to_markdown() method
    return markdown

# Iterate over all PDFs in the input directory
for pdf_file in os.listdir(input_dir):
    if pdf_file.endswith(".pdf"):
        try:
            # Define the output Markdown file path
            md_file = os.path.join(output_dir, os.path.splitext(pdf_file)[0] + ".md")
            
            # Extract text from the PDF
            pdf_path = os.path.join(input_dir, pdf_file)
            text = extract_text_from_pdf(pdf_path)
            
            # Convert the text to Markdown using docling
            markdown = text_to_markdown(text)
            
            # Save the Markdown file
            with open(md_file, "w", encoding="utf-8") as md_file:
                md_file.write(markdown)
            
            print(f"Converted {pdf_file} to {md_file}")
        except Exception as e:
            print(f"Skipping {pdf_file} due to error: {e}")

print("Conversion complete!")