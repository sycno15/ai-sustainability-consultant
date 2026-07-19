from fastapi import APIRouter, Depends, BackgroundTasks, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.middleware.auth import get_current_user
from app.models.models import User
from app.schemas.report import ReportFeedbackCreate
from app.services.report_service import ReportService
from uuid import UUID

router = APIRouter(prefix="/reports", tags=["Report"])

@router.get("/{id}", response_model=None)
async def get_report(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = ReportService.get_report(db, current_user.id, id)
    return {
        "success": True,
        "data": result
    }

@router.post("/{id}/feedback", response_model=None)
async def submit_feedback(
    id: UUID,
    payload: ReportFeedbackCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = ReportService.submit_feedback(db, current_user.id, id, payload.feedback, background_tasks)
    return {
        "success": True,
        "data": result
    }

@router.post("/{id}/approve", response_model=None)
async def approve_report(
    id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = ReportService.approve_report(db, current_user.id, id, background_tasks)
    return {
        "success": True,
        "data": result
    }

@router.get("/{id}/pdf", response_model=None)
async def download_pdf(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pdf_url = ReportService.get_pdf(db, current_user.id, id)
    # Redirect the user to the Supabase storage signed URL/public URL
    return RedirectResponse(url=pdf_url)

@router.get("/{id}/json", response_model=None)
async def download_json(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report_json = ReportService.get_json(db, current_user.id, id)
    return {
        "success": True,
        "data": report_json
    }
