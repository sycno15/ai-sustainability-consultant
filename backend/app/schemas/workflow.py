from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class WorkflowStartData(BaseModel):
    status: str

class WorkflowStartResponse(BaseModel):
    success: bool
    data: WorkflowStartData

class WorkflowStatusData(BaseModel):
    status: str
    current_agent: Optional[str] = None
    progress: int
    retry_count: int

class WorkflowStatusResponse(BaseModel):
    success: bool
    data: WorkflowStatusData

class WorkflowTimelineItem(BaseModel):
    agent: str
    tool: str
    duration: float
    status: str

class WorkflowTimelineResponse(BaseModel):
    success: bool
    data: List[WorkflowTimelineItem]
