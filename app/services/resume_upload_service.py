from fastapi import UploadFile, HTTPException
import pymupdf


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
        doc=pymupdf.open(stream=pdf_bytes,filetype="pdf")

    except pymupdf.FileDataError:
        raise HTTPException(status_code=400,detail="Invalid or corrupted PDF file.")

    text = ""
    no_of_pages=0

    for page in doc:

        if no_of_pages>10:
            raise HTTPException(status_code=400,detail="Resume must not exceed 10 pages.")
        
        text+=page.get_text()
        text+="\n"
        no_of_pages+=1

    doc.close()

    text = text.strip()
    if not text:
        raise HTTPException(status_code=400,detail="Could not extract readable text from the PDF.")

    if len(text)>30000:
        raise HTTPException(status_code=400,detail="Resume text exceeds the maximum allowed length of 30,000 characters.")

    return {
        'text':text
    }