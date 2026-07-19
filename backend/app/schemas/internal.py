from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import UUID

class InternalOrchestratorStart(BaseModel):
    analysis_id: UUID

class InternalAgentRun(BaseModel):
    analysis_id: UUID
    shared_state: Optional[Dict[str, Any]] = None
