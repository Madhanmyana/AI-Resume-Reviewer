from fastapi import APIRouter, File, UploadFile

from services.resume_upload_service import upload_file

router = APIRouter()

@router.post('/upload')
async def resume(resume:UploadFile=File(...)):
    return await upload_file(resume)