from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from api.health import router as health_router
from api.api import router as all_apis
from limiter import limiter

app = FastAPI()
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)

#api routers
app.include_router(health_router)
app.include_router(all_apis)