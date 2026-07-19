from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.middleware.auth import get_current_user
from app.models.models import User
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardOverviewResponse, ReportsListResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=None)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    overview = DashboardService.get_dashboard_overview(db, current_user.id)
    return {
        "success": True,
        "data": overview
    }

@router.get("/reports", response_model=None)
async def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reports = DashboardService.get_reports_list(db, current_user.id)
    return {
        "success": True,
        "data": reports
    }
