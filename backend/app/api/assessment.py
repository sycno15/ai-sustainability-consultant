from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.middleware.auth import get_current_user
from app.models.models import User
from app.schemas.assessment import AssessmentCreate, AssessmentResponse, AssessmentDetailResponse
from app.services.assessment_service import AssessmentService
from uuid import UUID

router = APIRouter(prefix="/assessments", tags=["Assessment"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=None)
async def create_assessment(
    payload: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = AssessmentService.create_assessment(db, current_user.id, payload)
    return {
        "success": True,
        "data": result
    }

@router.get("/{id}", response_model=None)
async def get_assessment(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    details = AssessmentService.get_assessment(db, current_user.id, id)
    return {
        "success": True,
        "data": details
    }

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AssessmentService.delete_assessment(db, current_user.id, id)
    # 204 does not return content
    return None
