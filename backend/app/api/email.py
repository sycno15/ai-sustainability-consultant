from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.middleware.auth import get_current_user
from app.models.models import User
from app.services.email_service import EmailService
from app.services.report_service import ReportService
from uuid import UUID

router = APIRouter(prefix="/reports", tags=["Email"])

@router.post("/{id}/send-email", response_model=None)
async def send_email(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership of report before sending
    report = ReportService.get_report(db, current_user.id, id)
    if not report["approved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email can only be sent after report has been approved."
        )
        
    result = await EmailService.send_report_email(db, id, current_user.email)
    return {
        "success": True,
        "data": result
    }

@router.get("/{id}/email-status", response_model=None)
async def get_email_status(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = EmailService.get_email_status(db, current_user.id, id)
    return {
        "success": True,
        "data": result
    }
