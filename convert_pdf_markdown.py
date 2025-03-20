import logging
import time
from pathlib import Path
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# Constants
IMAGE_RESOLUTION_SCALE = 2.0

def main(pdf_path, service_type):
    logging.basicConfig(level=logging.INFO)

    input_doc_path = Path(pdf_path)
    output_dir = Path(f"output/{Path(pdf_path).stem}")

    # Configure pipeline options
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    # Convert the document
    conv_res = doc_converter.convert(input_doc_path)

    # Define job-specific folder based on PDF filename and service type
    job_folder = f"{conv_res.input.file.stem}-{service_type}"
    output_dir = output_dir / job_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save page images locally
    for page_no, page in conv_res.document.pages.items():
        page_image_filename = output_dir / f"{conv_res.input.file.stem}-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")
        logging.info(f"Saved page image: {page_image_filename}")

    # Save images of tables and figures locally
    table_counter = 0
    picture_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = output_dir / f"{conv_res.input.file.stem}-table-{table_counter}.png"
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")
            logging.info(f"Saved table image: {element_image_filename}")

        if isinstance(element, PictureItem):
            picture_counter += 1
            element_image_filename = output_dir / f"{conv_res.input.file.stem}-picture-{picture_counter}.png"
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")
            logging.info(f"Saved picture image: {element_image_filename}")

    # Save markdown with embedded images locally
    md_filename_embedded = output_dir / f"{conv_res.input.file.stem}-with-images.md"
    conv_res.document.save_as_markdown(md_filename_embedded, image_mode=ImageRefMode.EMBEDDED)
    logging.info(f"Saved Markdown with embedded images: {md_filename_embedded}")

    # Save markdown with externally referenced images locally
    md_filename_referenced = output_dir / f"{conv_res.input.file.stem}-with-image-refs.md"
    conv_res.document.save_as_markdown(md_filename_referenced, image_mode=ImageRefMode.REFERENCED)
    logging.info(f"Saved Markdown with referenced images: {md_filename_referenced}")

    end_time = time.time() - start_time
    logging.info(f"Document converted and saved in {end_time:.2f} seconds. Files stored in: {output_dir}")

# Example usage
if __name__ == "__main__":
    pdf_path = "/Users/kaushikj/Desktop/Assignment4-2/NVIDIA-PDFs/10K10-Q2-2024.pdf"  # Replace with the path to your PDF file
    service_type = "/Users/kaushikj/Desktop/Assignment4-2"  # Replace with your service type
    main(pdf_path, service_type)