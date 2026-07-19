from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.business_repository import BusinessRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.assessment import AssessmentCreate
from uuid import UUID
from typing import Dict, Any

class AssessmentService:
    @staticmethod
    def create_assessment(db: Session, user_id: UUID, payload: AssessmentCreate) -> Dict[str, Any]:
        # 1. Validate industry exists
        if not BusinessRepository.industry_exists(db, payload.industry):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Industry '{payload.industry}' is invalid or does not exist."
            )
            
        try:
            # 2. Create business profile
            profile = BusinessRepository.create_profile(
                db=db,
                user_id=user_id,
                business_name=payload.business_name,
                industry=payload.industry,
                company_size=payload.company_size.value,
                description=payload.description
            )
            
            # 3. Create metrics
            BusinessRepository.create_metrics(
                db=db,
                business_id=profile.id,
                electricity_usage=payload.electricity_usage,
                diesel_usage=payload.diesel_usage,
                petrol_usage=payload.petrol_usage,
                water_usage=payload.water_usage,
                waste_generated=payload.waste_generated,
                annual_revenue=payload.annual_revenue,
                sustainability_budget=payload.sustainability_budget
            )
            
            # 4. Create analysis with structured goals in shared_state
            goals = {
                "reduction_goal": float(payload.reduction_goal or 20),
                "priority": payload.priority or "ROI",
                "timeline_months": int(payload.timeline_months or 12),
                "notes": payload.notes or "",
            }
            analysis = WorkflowRepository.create_analysis(
                db=db,
                business_id=profile.id,
                shared_state={"goals": goals},
            )
            
            return {
                "assessment_id": analysis.id,
                "workflow_status": analysis.workflow_status
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create assessment: {str(e)}"
            )

    @staticmethod
    def get_assessment(db: Session, user_id: UUID, analysis_id: UUID) -> Dict[str, Any]:
        analysis = WorkflowRepository.get_analysis_by_id(db, analysis_id)
        if not analysis or not analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
            
        if analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this assessment"
            )
            
        profile = analysis.business
        metrics = BusinessRepository.get_metrics_by_business_id(db, profile.id)
        
        return {
            "id": profile.id,
            "business_name": profile.business_name,
            "industry": profile.industry,
            "company_size": profile.company_size,
            "description": profile.description,
            "metrics": metrics
        }

    @staticmethod
    def delete_assessment(db: Session, user_id: UUID, analysis_id: UUID) -> None:
        analysis = WorkflowRepository.get_analysis_by_id(db, analysis_id)
        if not analysis or not analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
            
        if analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this assessment"
            )
            
        if analysis.workflow_status and analysis.workflow_status.upper() == "RUNNING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assessment cannot be deleted while workflow is running."
            )
            
        try:
            BusinessRepository.delete_profile(db, analysis.business)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete assessment: {str(e)}"
            )
