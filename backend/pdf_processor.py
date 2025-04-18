"""PDF processing utilities"""
from PyPDF2 import PdfReader
import io


def extract_text_from_pdf(pdf_stream: io.BytesIO) -> list[str]:
    """Extract text from PDF file and split into chunks."""
    # Create PDF reader object
    pdf_reader = PdfReader(pdf_stream)

    # Extract text from all pages
    text_chunks = []
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            # Split text into chunks of roughly 1000 characters
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            text_chunks.extend(chunks)

    return text_chunks
