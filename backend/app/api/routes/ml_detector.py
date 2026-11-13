
from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.schemas.ml_detector import (
    MLDetectionRequest,
    MLDetectionResponse,
)
from app.services.ml_detector_service import detect_ai_text


router = APIRouter(
    dependencies=[Depends(get_current_user)]
)


@router.post(
    "/detect",
    response_model=MLDetectionResponse,
    status_code=200,
)
def detect_text(payload: MLDetectionRequest):
    result = detect_ai_text(payload.text)
    return result
