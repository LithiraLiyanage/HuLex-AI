from fastapi import FastAPI
from app.api.routes import ml_detector
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.documents import router as documents_router
from app.api.routes.analysis import router as analysis_router

app = FastAPI(
    title="HumanFlow AI API",
    description="Backend API for intelligent text refinement and style adaptation.",
    version="0.1.0"
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(analysis_router)
app.include_router(
    ml_detector.router,
    prefix="/api/ml",
    tags=["ML Detector"],
)

@app.get("/")
def root():
    return {
        "message": "Welcome to HumanFlow AI",
        "status": "running"
    }
from app.api.routes import rewrite_studio
from app.ui import mount_site
app.include_router(rewrite_studio.router, prefix='/api/rewrite', tags=['Writing Studio'])
mount_site(app)

