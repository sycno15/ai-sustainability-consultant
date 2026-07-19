from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EmailStatusData(BaseModel):
    status: str
    recipient: EmailStr
    sent_at: Optional[datetime] = None

class EmailStatusResponse(BaseModel):
    success: bool
    data: EmailStatusData

class EmailSendResponseData(BaseModel):
    delivery_status: str

class EmailSendResponse(BaseModel):
    success: bool
    data: EmailSendResponseData
