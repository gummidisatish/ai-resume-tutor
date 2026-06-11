from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.jobs import router as jobs_router
from app.api.matches import router as matches_router
from app.api.resumes import router as resumes_router
from app.api.ats import router as ats_router
from app.api.tutor import router as tutor_router


app = FastAPI(
    title="AI Resume Parser and Tutor API",
    description="Full-stack AI Resume Parser with an AI Course Tutor",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://ai-resume-tutor-9makrmcgj-satish-kumar-s-projects3.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(matches_router)
app.include_router(ats_router)
app.include_router(tutor_router)

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "AI Resume Parser backend is running"
    }


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "message": "Backend connected successfully",
    }