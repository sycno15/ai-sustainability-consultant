from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class DashboardOverviewData(BaseModel):
    total_reports: int
    latest_score: Optional[float] = None
    email_status: Optional[str] = None

class DashboardOverviewResponse(BaseModel):
    success: bool
    data: DashboardOverviewData

class ReportItem(BaseModel):
    id: UUID
    business_name: str
    industry: str
    overall_score: Optional[float] = None
    approved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ReportsListResponse(BaseModel):
    success: bool
    data: List[ReportItem]
