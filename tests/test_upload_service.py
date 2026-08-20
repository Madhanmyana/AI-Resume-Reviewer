"""
PHASE 4: File Validation & PDF Processing Tests
=================================================

These are UNIT TESTS for the upload_file() function in resume_upload_service.py.

WHY test file validation?
  It's your first line of defense against bad input. Each validation
  prevents a different class of problem (wrong type, corrupted file,
  oversized content, etc.). These tests are fast and need no external services.

The upload_file() function has 8 distinct validations.
We test each one to ensure it rejects bad input with the correct
HTTP status code and error message.

TEACHING NOTE — Testing async functions:
  upload_file() is defined with "async def", so we must "await" it.
  pytest-asyncio (configured with asyncio_mode=auto in pytest.ini)
  lets us write "async def test_*" functions that pytest runs in an event loop.
"""

import pytest
import pymupdf
from unittest.mock import MagicMock
from fastapi import HTTPException
from io import BytesIO

from services.resume_upload_service import upload_file


# ─── Helpers ────────────────────────────────────────────────────────────

def _make_upload_file(content: bytes, content_type: str = "application/pdf",
                      filename: str = "resume.pdf"):
    """
    Creates an UploadFile for testing.

    TEACHING NOTE:
    UploadFile is what FastAPI gives you when someone uploads a file.
    For testing, we create one manually with controlled content so we
    can test every validation branch without needing real user files.
    """
    from fastapi import UploadFile
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers={"content-type": content_type},
    )


def _create_valid_pdf(text: str = "Sample resume content") -> bytes:
    """Creates a minimal valid PDF using PyMuPDF."""
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=10)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


# ═══════════════════════════════════════════════════════════════════════════
# Validation Tests — one test per validation rule
# ═══════════════════════════════════════════════════════════════════════════


async def test_rejects_non_pdf_content_type():
    """
    VALIDATION 1: content_type must be "application/pdf"

    Arrange: UploadFile with content_type="text/plain"
    Act:     Call upload_file()
    Assert:  HTTPException 400 with "Only PDF files are allowed."

    WHY: The app only processes PDFs. Accepting other types would crash
    the PDF parser downstream.
    """
    fake_file = _make_upload_file(b"not a pdf", content_type="text/plain")

    with pytest.raises(HTTPException) as exc_info:
        await upload_file(fake_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Only PDF files are allowed."


async def test_rejects_empty_file():
    """
    VALIDATION 2: File must not be empty (0 bytes)

    WHY: An empty file has no content to extract — fail fast.
    """
    fake_file = _make_upload_file(b"", content_type="application/pdf")

    with pytest.raises(HTTPException) as exc_info:
        await upload_file(fake_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Uploaded PDF is empty."


async def test_rejects_invalid_pdf_magic_bytes():
    """
    VALIDATION 3: File must start with the %PDF- magic bytes

    WHY: Someone might rename a .txt file to .pdf. The magic bytes
    check catches this before we even try to parse the PDF.
    """
    fake_file = _make_upload_file(
        b"This is definitely not a PDF file",
        content_type="application/pdf",
    )

    with pytest.raises(HTTPException) as exc_info:
        await upload_file(fake_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid PDF file."


async def test_rejects_oversized_file():
    """
    VALIDATION 4: File must not exceed 5 MB (5,242,880 bytes)

    WHY: Large files waste memory and processing time.
    We create bytes with a valid %PDF- header but exceeding 5 MB.
    """
    oversized = b"%PDF-" + b"x" * (5 * 1024 * 1024 + 1)
    fake_file = _make_upload_file(oversized, content_type="application/pdf")

    with pytest.raises(HTTPException) as exc_info:
        await upload_file(fake_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "PDF file size must not exceed 5 MB."


async def test_rejects_corrupted_pdf():
    """
    VALIDATION 5: pymupdf.FileDataError on corrupted PDF

    WHY: A file starting with %PDF- but containing garbage data will cause
    PyMuPDF to raise FileDataError. The app catches this gracefully.
    """
    corrupted = b"%PDF-1.4 this is corrupted garbage data"
    fake_file = _make_upload_file(corrupted, content_type="application/pdf")

    with pytest.raises(HTTPException) as exc_info:
        await upload_file(fake_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid or corrupted PDF file."


async def test_rejects_pdf_with_too_many_pages():
    """
    VALIDATION 6: Page count must not exceed 10

    WHY: Resumes shouldn't be 12 pages. This prevents abuse and controls
    LLM input size.

    NOTE — Off-by-one in the actual code:
    The code checks `if no_of_pages > 10` BEFORE incrementing, and the
    counter starts at 0. This means 11 pages are actually ALLOWED
    (the error only triggers on the 12th page). We test the ACTUAL
    behavior — 12 pages fails.
    """
    doc = pymupdf.open()
    for i in range(12):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {i + 1} content")
    pdf_bytes = doc.tobytes()
    doc.close()

    fake_file = _make_upload_file(pdf_bytes, content_type="application/pdf")

    with pytest.raises(HTTPException) as exc_info:
        await upload_file(fake_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Resume must not exceed 10 pages."


async def test_rejects_pdf_with_no_extractable_text():
    """
    VALIDATION 7: Extracted text must not be empty after strip()

    WHY: A valid PDF with no text (e.g., scanned image with no OCR)
    is useless for LLM review. Fail with a helpful message.
    """
    doc = pymupdf.open()
    doc.new_page()  # Empty page — no text inserted
    pdf_bytes = doc.tobytes()
    doc.close()

    fake_file = _make_upload_file(pdf_bytes, content_type="application/pdf")

    with pytest.raises(HTTPException) as exc_info:
        await upload_file(fake_file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Could not extract readable text from the PDF."


async def test_rejects_pdf_with_text_exceeding_30000_chars(monkeypatch):
    """
    VALIDATION 8: Extracted text must not exceed 30,000 characters

    WHY: Controls LLM token usage and prevents abuse.

    TEACHING NOTE — monkeypatch:
    Instead of creating a real PDF with 30,000+ characters of text
    (which would be slow and memory-heavy), we use monkeypatch to
    replace pymupdf.open() with a fake that returns controllable text.
    This isolates the test to ONLY the text-length check.

    monkeypatch is a pytest built-in fixture that lets you temporarily
    replace attributes, environment variables, or dict items. Changes
    are automatically reverted after the test.
    """
    long_text = "a" * 30001

    # IMPORTANT: Create the valid PDF BEFORE monkeypatching pymupdf.open,
    # because _create_valid_pdf() also uses pymupdf.open internally!
    valid_pdf = _create_valid_pdf("dummy")
    fake_file = _make_upload_file(valid_pdf, content_type="application/pdf")

    # Create a mock page that returns our long text
    mock_page = MagicMock()
    mock_page.get_text.return_value = long_text

    # Create a mock document that iterates over one page
    mock_doc = MagicMock()
    mock_doc.__iter__ = lambda self: iter([mock_page])

    # NOW replace pymupdf.open so upload_file() sees our mock document
    monkeypatch.setattr(
        "services.resume_upload_service.pymupdf.open",
        lambda **kwargs: mock_doc,
    )

    with pytest.raises(HTTPException) as exc_info:
        await upload_file(fake_file)

    assert exc_info.value.status_code == 400
    assert "30,000 characters" in exc_info.value.detail


# ═══════════════════════════════════════════════════════════════════════════
# Happy Path — valid PDF succeeds
# ═══════════════════════════════════════════════════════════════════════════


async def test_valid_pdf_returns_extracted_text():
    """
    HAPPY PATH: A valid PDF with text should return {'text': <extracted text>}.

    This is the most important test — it proves the function WORKS
    when given correct input.
    """
    pdf_bytes = _create_valid_pdf("John Doe\nSoftware Engineer")
    fake_file = _make_upload_file(pdf_bytes, content_type="application/pdf")

    result = await upload_file(fake_file)

    assert isinstance(result, dict)
    assert "text" in result
    assert "John Doe" in result["text"]
    assert "Software Engineer" in result["text"]
