import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Rewrite(Base):
    __tablename__ = "rewrites"

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

    rewritten_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    target_tone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    target_audience: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    humanization_level: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False
    )

    semantic_similarity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    fact_preservation_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    model_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    document = relationship(
        "Document",
        back_populates="rewrites"
    )