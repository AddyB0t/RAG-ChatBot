from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limiter import RateLimitMiddleware
from app.api.routes import health, resumes, errors, job_matching, quality_analysis, advanced_features

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Resume Parser & Job Matcher",
    description="Complete resume analysis platform with AI-powered parsing, job matching, quality analysis, and advanced features",
    version="2.2.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 70)
    logger.info("🚀 AI-Powered Resume Parser & Job Matcher v2.2.0")
    logger.info("=" * 70)
    logger.info("📊 Database: Connected")
    logger.info("🔌 API: Ready")
    logger.info("")
    logger.info("ℹ️  ML Models will download on first use:")
    logger.info("   • Flair NER (~500MB) - downloads when first resume is uploaded")
    logger.info("   • This is normal and only happens once")
    logger.info("")
    logger.info("📚 API Documentation: http://localhost:8000/docs")
    logger.info("=" * 70)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit)

app.include_router(health.router)
app.include_router(resumes.router)
app.include_router(errors.router)
app.include_router(job_matching.router)
app.include_router(quality_analysis.router)
app.include_router(advanced_features.router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )

