from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SavedDocumentCreate(BaseModel):
    document_type_name: str = Field(min_length=1, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=200_000)


class SavedDocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_type_name: str
    title: str
    created_at: datetime


class SavedDocumentOut(SavedDocumentSummary):
    content: str
