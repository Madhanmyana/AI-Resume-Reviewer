import os
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware

from api.health import router as health_router
from api.api import router as all_apis
from limiter import limiter

app = FastAPI()

origins = ["http://localhost:5173","https://ai-resume-reviewer.vercel.app"]

frontend_url = os.environ.get("FRONTEND_URL")

if frontend_url:
    origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

#api routers
app.include_router(health_router)
app.include_router(all_apis)