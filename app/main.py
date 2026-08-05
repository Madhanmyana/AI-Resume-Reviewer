from fastapi import FastAPI

from api.health import router as health_router
from api.api import router as all_apis

app = FastAPI()

#api routers
app.include_router(health_router)
app.include_router(all_apis)