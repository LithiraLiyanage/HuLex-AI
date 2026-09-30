from fastapi import FastAPI
from app.api.routes.health import router as health_router

app = FastAPI(
    title="HumanFlow AI API",
    description="Backend API for intelligent text refinement and style adaptation.",
    version="0.1.0"
)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to HumanFlow AI",
        "status": "running"
    }