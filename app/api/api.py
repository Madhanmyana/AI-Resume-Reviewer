from fastapi import APIRouter, File, UploadFile,Request
from typing import Optional

from services.resume_upload_service import upload_file
from services.resume_improvement_service import improve_resume
from services.resume_review_service import review_response
from limiter import limiter
from schemas.resume_review_schema import ResumeReviewResponse
from schemas.resume_analysis_response_schema import ResumeAnalysisResponse

router = APIRouter()

@router.post("/review-resume",response_model=ResumeAnalysisResponse)
@limiter.limit("5/minute")
async def review_resume(request: Request,target_role:Optional[str]=None, resume:UploadFile=File(...)):

    resume_text = await upload_file(resume)

    review = review_response(str(resume_text),target_role)

    improvements = improve_resume(str(resume_text), review, target_role)

    return {
        'review':review,
        'improvements':improvements
    }