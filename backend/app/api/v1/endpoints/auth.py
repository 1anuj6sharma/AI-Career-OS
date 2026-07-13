from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/health")
def auth_health():
    """
    Authentication module health check.
    """
    return {
        "module": "Authentication",
        "status": "running",
    }
