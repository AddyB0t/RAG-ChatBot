from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/")
async def root():
    return {"message": "AI-Powered Resume Parser API", "version": "1.0.0"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Resume parser system operational"}

