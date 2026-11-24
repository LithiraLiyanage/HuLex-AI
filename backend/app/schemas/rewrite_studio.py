"""Rewrite API schema (separate from the project's existing Rewrite DB model)."""
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class RewriteStudioRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=20000)
    tone: Literal['Natural', 'Professional', 'Friendly', 'Concise'] = 'Natural'
    length: Literal['Balanced', 'Shorter', 'Expanded'] = 'Balanced'

    @field_validator('text')
    @classmethod
    def ensure_words(cls, value: str) -> str:
        if len(value.split()) < 3:
            raise ValueError('Please provide a sentence with at least 3 words.')
        return value.strip()


class RewriteStudioResponse(BaseModel):
    rewritten_text: str
    mode: Literal['local_polish', 'model_rewrite']
    notes: str
