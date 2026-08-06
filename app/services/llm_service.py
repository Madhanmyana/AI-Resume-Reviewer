from openai import OpenAI
import openai
import os
from dotenv import load_dotenv

from prompts.resume_review_prompt import prompt

load_dotenv()

client=OpenAI(api_key=os.getenv("GROQ_API_KEY"),base_url="https://api.groq.com/openai/v1")

def review_response(resume_text:str):

    final_prompt = prompt + "resume starts here" + resume_text + "resume ends here"

    try:
        response=client.responses.create(model="openai/gpt-oss-20b",input=final_prompt)
        return response.output_text
    except openai.error.apierror as e:
        print(f"openai returned an api error:"{e})
    except openai.error.apiconnectionerror as e:
        print(f"openai api request failed to connect:"{e})