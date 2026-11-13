
from pydantic import BaseModel, Field, field_validator


class MLDetectionRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=20000,
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = " ".join(value.split())

        if len(value.split()) < 30:
            raise ValueError(
                "Please provide at least 30 words."
            )

        return value


class MLDetectionResponse(BaseModel):
    predicted_label: str
    ai_likelihood: float
    human_likelihood: float
    model: str
    warning: str
