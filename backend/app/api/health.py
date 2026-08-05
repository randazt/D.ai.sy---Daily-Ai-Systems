from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "D.AI.SY Backend",
        "version": "0.1.0"
    }