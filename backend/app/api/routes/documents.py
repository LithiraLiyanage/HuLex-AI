import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.services.document_service import (
    create_document,
    delete_document,
    get_user_document,
    get_user_documents,
    update_document,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_document(
    data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_document(
        db,
        current_user.id,
        data
    )


@router.get(
    "",
    response_model=list[DocumentResponse]
)
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_documents(
        db,
        current_user.id
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse
)
def get_document(
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

    return document


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse
)
def edit_document(
    document_id: uuid.UUID,
    data: DocumentUpdate,
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

    return update_document(
        db,
        document,
        data
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_document(
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

    delete_document(
        db,
        document
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )