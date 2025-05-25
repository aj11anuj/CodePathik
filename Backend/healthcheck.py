from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def health_check():
    return {"status": "ok", "service": "codepathik"}
