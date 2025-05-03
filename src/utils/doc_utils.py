from fastapi import UploadFile
import fitz
import aiofiles
from io import BytesIO
from src.types.pipecode_data_types import QueryResult, TextData
from src.utils.ocr_utils import extract_imag_text
from src.providers.pinecone import PineconeClient
from src.utils.config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from PIL import Image
from loguru import logger
from pathlib import Path


async def process_file_document(file_data: bytes, filename: str):
    """
    Process file document to extract text and upsert to Pinecone
    """
    # Determine if the file is a PDF or an image
    if filename.lower().endswith(".pdf"):
        logger.info(f"Processing PDF file {filename}")

        # Open the PDF using fitz (PyMuPDF)
        pdf_document = fitz.open(stream=BytesIO(file_data))
        extracted_text = []

        for page in pdf_document:
            pix = page.get_pixmap(dpi=500)

            # Convert pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.w, pix.h], pix.samples)

            # Save the image to a BytesIO buffer as PNG
            image_bytes = BytesIO()
            img.save(image_bytes, "PNG")  # Save the image to the BytesIO stream
            image_bytes.seek(0)

            # Example usage:
            image_data = image_bytes.read()

            extracted_text += await extract_imag_text(image_data)
    else:
        # For images, directly extract text
        logger.info(f"Processing image file {filename}")
        extracted_text = await extract_imag_text(file_data)

    text_data = TextData(
        id=str(filename),
        text=" ".join(extracted_text),
    )

    # Initialize Pinecone client
    pinecone_client = PineconeClient(
        api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME
    )

    # Upsert vectors into Pinecone
    await pinecone_client.upsert_vectors([text_data])
    logger.info(f"Text data from file '{filename}' successfully upserted to Pinecone.")


async def get_chuncks_similar_to_text(text: str) -> QueryResult | None:
    """
    Do similarity search for the given text to get matched chucks from pinecone
    """
    # Initialize Pinecone client
    pinecone_client = PineconeClient(
        api_key=PINECONE_API_KEY, index_name=PINECONE_INDEX_NAME
    )

    # Query the index with the search query
    query_results = await pinecone_client.query(text)

    # Return the results as a response
    return query_results


async def save_file(file: UploadFile, directory: str = "uploads") -> str:
    """
    Save the uploaded file to the specified directory.

    Args:
    - file: The uploaded file.
    - directory: Directory where the file should be saved (default is 'data').

    Returns:
    - The file path where the file was saved.
    """
    # Ensure the directory exists
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)

    # Define the file path where the file will be saved
    file_path = dir_path / file.filename

    try:
        # Open the file asynchronously and write the content
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())

        return str(file_path)  # Return the file path after saving

    except Exception as e:

        raise Exception(f"Error saving file: {e}") from e
