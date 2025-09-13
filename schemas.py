from pydantic import BaseModel, Field
from datetime import datetime

class CardCreate(BaseModel):
    column_id: int
    parent_id: int | None = None
    title: str = Field(..., min_length=1)
    notes: str = ""
    due_at: datetime | None = None

class CardUpdate(BaseModel):
    title: str | None = None
    notes: str | None = None
    due_at: datetime | None = None
    column_id: int | None = None
    parent_id: int | None = None
    position: int | None = None

class ChecklistCreate(BaseModel):
    text: str
