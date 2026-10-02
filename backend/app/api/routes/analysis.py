import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.deps import get_db
from app.models.analysis_result import AnalysisResult
from app.models.user import User
from app.schemas.analysis import AnalysisResponse
from app.services.document_service import get_user_document
from app.services.text_analysis_service import analyze_document


router = APIRouter(
    prefix="/api/analysis",
    tags=["Text Analysis"]
)


@router.post(
    "/{document_id}",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED
)
def analyze_document_endpoint(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = get_user_document(
        db,
        current_user.id,
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    return analyze_document(
        db,
        document
    )


@router.get(
    "/{document_id}",
    response_model=list[AnalysisResponse]
)
def get_analysis_history(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = get_user_document(
        db,
        current_user.id,
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    statement = (
        select(AnalysisResult)
        .where(
            AnalysisResult.document_id == document.id
        )
        .order_by(
            AnalysisResult.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )