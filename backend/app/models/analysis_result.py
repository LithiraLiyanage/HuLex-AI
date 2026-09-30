import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    detected_tone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    detected_audience: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    readability_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    naturalness_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    robotic_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    semantic_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    analysis_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    document = relationship(
        "Document",
        back_populates="analysis_results"
    )