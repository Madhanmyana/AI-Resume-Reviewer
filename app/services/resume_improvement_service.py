import openai
from fastapi import HTTPException

from services.resume_review_service import client
from schemas.resume_review_schema import ResumeReviewResponse
from schemas.resume_improvement_schema import ResumeImprovementResponse
from schemas.resume_analysis_response_schema import ResumeAnalysisResponse 
from prompts.resume_improvement_prompt import prompt, target_role_prompt

def improve_resume(resume_text:str, ResumeReviewResponse:ResumeReviewResponse ,target_role: str | None = None):

    final_prompt = prompt + "resume starts here" + resume_text + "resume ends here" + "resume review starts here" + str(ResumeReviewResponse) + "resume review ends here"
    
    if target_role:
        final_prompt = prompt + "resume starts here" + resume_text + "resume ends here" + "resume review starts here" + str(ResumeReviewResponse) + "resume review ends here" + target_role_prompt + target_role

    try:
        response=client.responses.parse(model="openai/gpt-oss-20b",input=final_prompt,text_format=ResumeImprovementResponse,reasoning={"effort": "low"},max_output_tokens=4000)
        return response.output_parsed

    except openai.AuthenticationError:
        raise HTTPException(status_code=500,detail="Our Groq API credentials are invalid")

    except openai.RateLimitError:
        raise HTTPException(status_code=429,detail="Groq has rate-limited us")
    
    except openai.APIConnectionError:
        raise HTTPException(status_code=500,detail='connection error, check internet')

    except openai.APIError as e:
        print(f"Groq API error: {e}")
        raise HTTPException(status_code=500,detail='AI service is temporarily unavailable. Please try again later.')