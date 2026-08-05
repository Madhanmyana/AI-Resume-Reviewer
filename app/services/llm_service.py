from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client=OpenAI(api_key=os.getenv("GROQ_API_KEY"),base_url="https://api.groq.com/openai/v1")

def llm_response(request):

    response=client.reponses.create(model="openai/gpt-oss-20b",input=request)

    return{
        "response":response
    }