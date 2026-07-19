from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID

class ReportFeedbackCreate(BaseModel):
    feedback: str = Field(..., min_length=1, max_length=2000, description="Feedback text is required and max 2000 characters")

class ReportResponseData(BaseModel):
    id: UUID
    analysis_id: UUID
    report_json: Dict[str, Any]
    pdf_url: Optional[str] = None
    approved: bool
    overall_score: Optional[float] = None

class ReportResponse(BaseModel):
    success: bool
    data: ReportResponseData

class ReportApprovalData(BaseModel):
    report_status: str
    email_status: str

class ReportApprovalResponse(BaseModel):
    success: bool
    data: ReportApprovalData
