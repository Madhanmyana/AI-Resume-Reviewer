from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from typing import Optional

from prompts.resume_review_prompt import prompt, target_role_prompt
from schemas.resume_review_schema import ResumeReviewResponse

load_dotenv()

client=OpenAI(api_key=os.getenv("GROQ_API_KEY"),base_url="https://api.groq.com/openai/v1")

def review_response(resume_text:str, target_role:str|None = None):

    final_prompt = prompt + "resume starts here" + resume_text + "resume ends here"

    if target_role:
        final_prompt = prompt + "resume starts here" + resume_text + "resume ends here" + target_role_prompt + target_role

    try:
        response=client.responses.parse(model="openai/gpt-oss-20b",input=final_prompt,text_format=ResumeReviewResponse,reasoning={"effort": "low"},max_output_tokens=4000)
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
