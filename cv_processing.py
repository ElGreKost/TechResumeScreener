# cv_processing.py
import os
import fitz  # PyMuPDF
from openai_interaction import extract_information_from_cv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_pages_as_images(pdf_bytes, output_folder="temp_images"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_paths = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_index in range(len(doc)):
                page = doc[page_index]
                # Render page to an image (pixmap)
                pix = page.get_pixmap()
                # Define the image path
                image_path = os.path.join(output_folder, f"page_{page_index + 1}.png")
                # Save the image
                pix.save(image_path)
                image_paths.append(image_path)
    except Exception as e:
        logger.error(f"Error rendering PDF pages to images: {e}")
    return image_paths

def extract_hyperlinks(pdf_bytes):
    """
    Extract all hyperlinks from the PDF.
    """
    hyperlinks = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                links = page.get_links()
                for link in links:
                    uri = link.get("uri", "")
                    if uri:
                        hyperlinks.append(uri)
    except Exception as e:
        logger.error(f"Error extracting hyperlinks: {e}")
    return hyperlinks

def process_cv(file_bytes, api_params):
    try:
        # Save pages as images
        image_paths = save_pages_as_images(file_bytes)
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return {}, "", []

    if not image_paths:
        logger.error("No pages were converted to images.")
        return {}, "", []

    extracted_info_list = []
    cv_summaries = []
    for image_path in image_paths:
        try:
            # Extract information from the CV image
            extracted_info, cv_summary = extract_information_from_cv(image_path, api_params)
            extracted_info_list.append(extracted_info)
            cv_summaries.append(cv_summary)
        except Exception as e:
            logger.error(f"Error extracting information from CV image: {e}")
            continue

    # Combine extracted information and summaries from all pages
    combined_extracted_info = {}
    for info in extracted_info_list:
        combined_extracted_info.update(info)

    combined_cv_summary = " ".join(cv_summaries)

    # Extract hyperlinks from the PDF
    hyperlinks = extract_hyperlinks(file_bytes)

    # Clean up temporary images
    for image_path in image_paths:
        os.remove(image_path)
    os.rmdir("temp_images")

    return combined_extracted_info, combined_cv_summary, hyperlinks
