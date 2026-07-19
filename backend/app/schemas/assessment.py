from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from enum import Enum

class CompanySizeEnum(str, Enum):
    Small = "Small"
    Medium = "Medium"
    Large = "Large"

class AssessmentCreate(BaseModel):
    business_name: str = Field(..., min_length=1, description="Business name is required")
    industry: str = Field(..., min_length=1, description="Industry is required")
    company_size: CompanySizeEnum = Field(..., description="Company size must be Small, Medium, or Large")
    description: Optional[str] = Field(None, max_length=1000)
    
    electricity_usage: float = Field(0.0, ge=0.0, description="Electricity usage must be a positive number")
    diesel_usage: float = Field(0.0, ge=0.0, description="Diesel usage must be a positive number")
    petrol_usage: float = Field(0.0, ge=0.0, description="Petrol usage must be a positive number")
    water_usage: float = Field(0.0, ge=0.0, description="Water usage must be a positive number")
    waste_generated: float = Field(0.0, ge=0.0, description="Waste generated must be a positive number")
    
    annual_revenue: float = Field(0.0, ge=0.0, description="Annual revenue must be a positive number")
    sustainability_budget: float = Field(0.0, ge=0.0, description="Sustainability budget must be a positive number")

    reduction_goal: Optional[float] = Field(20.0, ge=0.0, le=100.0)
    priority: Optional[str] = Field("ROI")
    timeline_months: Optional[int] = Field(12, ge=1)
    notes: Optional[str] = Field(None, max_length=500)

class AssessmentResponseData(BaseModel):
    assessment_id: UUID
    workflow_status: str

class AssessmentResponse(BaseModel):
    success: bool
    data: AssessmentResponseData

class AssessmentMetricDetail(BaseModel):
    electricity_usage: float
    diesel_usage: float
    petrol_usage: float
    water_usage: float
    waste_generated: float
    annual_revenue: float
    sustainability_budget: float

    class Config:
        from_attributes = True

class AssessmentDetailData(BaseModel):
    id: UUID
    business_name: str
    industry: str
    company_size: str
    description: Optional[str] = None
    metrics: Optional[AssessmentMetricDetail] = None

class AssessmentDetailResponse(BaseModel):
    success: bool
    data: AssessmentDetailData
