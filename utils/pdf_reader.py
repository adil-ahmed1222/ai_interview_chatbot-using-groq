"""Extract text from PDF resumes using PyPDF."""

import logging
from io import BytesIO
from typing import BinaryIO, Union

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file: Union[str, BinaryIO, BytesIO]) -> str:
    """
    Extract plain text from a PDF file path or file-like object.

    Args:
        file: Path string or binary stream (e.g. Streamlit UploadedFile).

    Returns:
        Concatenated text from all pages.

    Raises:
        ValueError: If no text could be extracted.
    """
    try:
        reader = PdfReader(file)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        full_text = "\n\n".join(pages).strip()
        if not full_text:
            raise ValueError(
                "No readable text found in PDF. The file may be scanned or image-only."
            )
        logger.info("Extracted %d characters from PDF (%d pages).", len(full_text), len(reader.pages))
        return full_text
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("PDF extraction failed.")
        raise RuntimeError(f"Failed to read PDF: {exc}") from exc
