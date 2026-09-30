import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate


def create_document(
    db: Session,
    user_id: uuid.UUID,
    data: DocumentCreate
) -> Document:

    document = Document(
        user_id=user_id,
        title=data.title,
        original_text=data.original_text,
        source_type=data.source_type
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_user_documents(
    db: Session,
    user_id: uuid.UUID
) -> list[Document]:

    statement = (
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )

    return list(db.scalars(statement).all())


def get_user_document(
    db: Session,
    user_id: uuid.UUID,
    document_id: uuid.UUID
) -> Document | None:

    statement = select(Document).where(
        Document.id == document_id,
        Document.user_id == user_id
    )

    return db.scalar(statement)


def update_document(
    db: Session,
    document: Document,
    data: DocumentUpdate
) -> Document:

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(document, field, value)

    db.commit()
    db.refresh(document)

    return document


def delete_document(
    db: Session,
    document: Document
) -> None:

    db.delete(document)
    db.commit()