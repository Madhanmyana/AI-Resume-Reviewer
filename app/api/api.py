from fastapi import APIRouter, File, UploadFile

from services.resume_upload_service import upload_file
from services.llm_service import review_response

router = APIRouter()

@router.post("/review-resume")
async def review_resume(resume:UploadFile=File(...)):

    resume_text = await upload_file(resume)

    return review_response(str(resume_text))