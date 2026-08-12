from fastapi import APIRouter, File, UploadFile,Request

from services.resume_upload_service import upload_file
from services.llm_service import review_response
from limiter import limiter

router = APIRouter()

@router.post("/review-resume")
@limiter.limit("5/minute")
async def review_resume(request: Request,resume:UploadFile=File(...)):

    resume_text = await upload_file(resume)

    return review_response(str(resume_text))