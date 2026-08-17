from pydantic import BaseModel

from schemas.resume_improvement_schema import ResumeImprovementResponse
from schemas.resume_review_schema import ResumeReviewResponse

class ResumeAnalysisResponse(BaseModel):
    review:ResumeReviewResponse
    improvements:ResumeImprovementResponse