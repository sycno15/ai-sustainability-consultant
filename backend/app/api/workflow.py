from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.middleware.auth import get_current_user
from app.models.models import User
from app.services.workflow_service import WorkflowService
from uuid import UUID

router = APIRouter(prefix="/analysis", tags=["Workflow"])

@router.post("/{id}/start", response_model=None)
async def start_workflow(
    id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = WorkflowService.start_analysis(db, current_user.id, id, background_tasks)
    return {
        "success": True,
        "data": result
    }

@router.get("/{id}/status", response_model=None)
async def get_workflow_status(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = WorkflowService.get_workflow_status(db, current_user.id, id)
    return {
        "success": True,
        "data": result
    }

@router.get("/{id}/timeline", response_model=None)
async def get_workflow_timeline(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = WorkflowService.get_timeline(db, current_user.id, id)
    return {
        "success": True,
        "data": result
    }
