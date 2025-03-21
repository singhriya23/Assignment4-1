import logging
import time
from pathlib import Path
from docling_core.types.doc import ImageRefMode
from docling.document_converter import DocumentConverter

def process_pdf(pdf_path, output_dir):
    """Process a single PDF file and save its Markdown output."""
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path(pdf_path)
    output_dir = Path(output_dir)

    # Initialize the DocumentConverter
    doc_converter = DocumentConverter()

    start_time = time.time()
    try:
        # Convert the document
        conv_res = doc_converter.convert(input_doc_path)

        # Ensure the output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save markdown with embedded images
        md_filename_embedded = output_dir / f"{input_doc_path.stem}-with-images.md"
        conv_res.document.save_as_markdown(md_filename_embedded, image_mode=ImageRefMode.EMBEDDED)
        logging.info(f"Saved Markdown with embedded images: {md_filename_embedded}")

        # Save markdown with externally referenced images
        md_filename_referenced = output_dir / f"{input_doc_path.stem}-with-image-refs.md"
        conv_res.document.save_as_markdown(md_filename_referenced, image_mode=ImageRefMode.REFERENCED)
        logging.info(f"Saved Markdown with referenced images: {md_filename_referenced}")

        end_time = time.time() - start_time
        logging.info(f"Document converted and saved in {end_time:.2f} seconds. Files stored in: {output_dir}")
    except Exception as e:
        logging.error(f"Failed to process {pdf_path}: {e}")

# Example usage
if __name__ == "__main__":
    pdf_path = "/Users/kaushikj/Desktop/Assignment4-2/pdf_reports/10K10-Q2-2024.pdf"  # Replace with the actual PDF file path
    output_dir = "/Users/kaushikj/Desktop/Assignment4-2/pdfs-done"  # Replace with your desired output folder
    process_pdf(pdf_path, output_dir)
