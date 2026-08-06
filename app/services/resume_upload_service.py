from fastapi import UploadFile, HTTPException
import pymupdf


async def upload_file(resume:UploadFile):

    if resume.content_type != "application/pdf":
        raise HTTPException(status_code=400,detail="Only PDF files are allowed.")

    pdf_bytes = await resume.read()

    doc=pymupdf.open(stream=pdf_bytes,filetype="pdf")

    text=""
    for page in doc:
        text+=page.get_text()
        text+="\n"

    doc.close()

    return {
        'text':text
    }