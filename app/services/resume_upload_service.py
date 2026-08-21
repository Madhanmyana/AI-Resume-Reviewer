from fastapi import UploadFile, HTTPException
import pypdf
import io

async def upload_file(resume:UploadFile):

    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400,detail="Only PDF files are allowed.")

    pdf_bytes = await resume.read()

    if not pdf_bytes:
        raise HTTPException(status_code=400,detail="Uploaded PDF is empty.")

    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(status_code=400,detail="Invalid PDF file.")

    if len(pdf_bytes)>5242880:
        raise HTTPException(status_code=400,detail="PDF file size must not exceed 5 MB.")

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    except Exception:
        raise HTTPException(status_code=400,detail="Invalid or corrupted PDF file.")

    text = ""
    no_of_pages = len(reader.pages)

    if no_of_pages > 10:
        raise HTTPException(status_code=400,detail="Resume must not exceed 10 pages.")

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    text = text.strip()
    if not text:
        raise HTTPException(status_code=400,detail="Could not extract readable text from the PDF.")

    if len(text)>30000:
        raise HTTPException(status_code=400,detail="Resume text exceeds the maximum allowed length of 30,000 characters.")

    return {
        'text':text
    }