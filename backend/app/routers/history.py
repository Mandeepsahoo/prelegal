from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..history_schemas import SavedDocumentCreate, SavedDocumentOut, SavedDocumentSummary
from ..models import SavedDocument, User
from .auth import get_current_user

router = APIRouter(prefix="/api/documents/history", tags=["history"])


@router.post("", response_model=SavedDocumentOut, status_code=status.HTTP_201_CREATED)
def save_document(
    payload: SavedDocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedDocumentOut:
    document = SavedDocument(
        user_id=current_user.id,
        document_type_name=payload.document_type_name,
        title=payload.title,
        content=payload.content,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return SavedDocumentOut.model_validate(document)


@router.get("", response_model=list[SavedDocumentSummary])
def list_saved_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SavedDocumentSummary]:
    documents = (
        db.query(SavedDocument)
        .filter(SavedDocument.user_id == current_user.id)
        .order_by(SavedDocument.created_at.desc())
        .all()
    )
    return [SavedDocumentSummary.model_validate(doc) for doc in documents]


@router.get("/{document_id}", response_model=SavedDocumentOut)
def get_saved_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedDocumentOut:
    document = db.get(SavedDocument, document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found.")
    return SavedDocumentOut.model_validate(document)
