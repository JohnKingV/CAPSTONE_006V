from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health", summary="Health")
def health():
    return {"status": "ok"}
