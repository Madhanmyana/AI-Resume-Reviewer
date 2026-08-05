from fastapi import APIRouter

from services.health_services import health

router=APIRouter()

@router.get('/health')
def health_api():
    return health()