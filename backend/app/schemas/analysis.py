import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalysisResponse(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    detected_tone: str | None
    detected_audience: str | None
    readability_score: float | None
    naturalness_score: float | None
    robotic_score: float | None
    semantic_score: float | None
    analysis_summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)