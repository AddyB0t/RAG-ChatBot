from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ResumeUploadResponse(BaseModel):
    id: str
    message: str
    filename: str
    status: str
    uploaded_at: datetime

class ResumeResponse(BaseModel):
    id: str
    file_name: str
    file_path: str
    file_size: int
    file_type: str
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    structured_data: Optional[dict] = None
    raw_text: Optional[str] = None

class ResumeStatusResponse(BaseModel):
    id: str
    status: str
    message: str
    processed_at: Optional[datetime] = None

