"""Authenticated HuLex writing refinement route."""
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import get_current_user
from app.schemas.rewrite_studio import RewriteStudioRequest, RewriteStudioResponse
from app.services.rewrite_studio_service import refine_text

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post('', response_model=RewriteStudioResponse)
def rewrite_text(payload: RewriteStudioRequest) -> dict:
    try:
        return refine_text(payload.text, payload.tone, payload.length)
    except (ValueError, RuntimeError) as err:
        # Deliberately avoids exposing provider responses, tokens, or prompt content.
        raise HTTPException(status_code=502, detail=str(err)) from err
