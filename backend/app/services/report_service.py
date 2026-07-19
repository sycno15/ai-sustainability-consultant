from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.repositories.report_repository import ReportRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.email_repository import EmailRepository
from uuid import UUID
from typing import Dict, Any
from app.config import settings, logger
import httpx

class ReportService:
    @staticmethod
    def get_report(db: Session, user_id: UUID, report_id: UUID) -> Dict[str, Any]:
        report = ReportRepository.get_report_by_id(db, report_id)
        if not report or not report.analysis or not report.analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
            
        if report.analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report"
            )
            
        return {
            "id": report.id,
            "analysis_id": report.analysis_id,
            "report_json": report.report_json,
            "pdf_url": report.pdf_url,
            "approved": report.approved,
            "overall_score": float(report.overall_score) if report.overall_score is not None else None
        }

    @staticmethod
    def submit_feedback(
        db: Session,
        user_id: UUID,
        report_id: UUID,
        feedback_text: str,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        report = ReportRepository.get_report_by_id(db, report_id)
        if not report or not report.analysis or not report.analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
            
        if report.analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
            
        if report.approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approved reports cannot be modified or revised."
            )
            
        # 1. Save feedback
        ReportRepository.create_feedback(db, report_id, feedback_text)
        
        # 2. Update analysis status to RUNNING to trigger replanning/revision loop
        # We also reset the current_agent to "Critic Agent" or let the orchestrator route it
        WorkflowRepository.update_analysis_status(
            db=db,
            analysis_id=report.analysis_id,
            workflow_status="RUNNING",
            current_agent="Critic Agent"
        )
        
        # Trigger background orchestrator to process revision feedback
        background_tasks.add_task(ReportService._trigger_orchestrator_revision, report.analysis_id)
        
        return {
            "status": "RUNNING"
        }

    @staticmethod
    def approve_report(
        db: Session,
        user_id: UUID,
        report_id: UUID,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        report = ReportRepository.get_report_by_id(db, report_id)
        if not report or not report.analysis or not report.analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
            
        if report.analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
            
        # If already approved, return existing status directly to prevent double approval
        if report.approved:
            return {
                "report_status": "APPROVED",
                "email_status": "SENDING"
            }
            
        # Update report status and lock it
        # For PDF URL, we will set a placeholder for Supabase Storage which will be generated
        pdf_filename = f"report_{report_id}.pdf"
        placeholder_pdf_url = f"{settings.SUPABASE_URL}/storage/v1/object/private/reports/{pdf_filename}"
        
        ReportRepository.approve_report(db, report_id, placeholder_pdf_url)
        
        # Update workflow/analysis status to APPROVED
        WorkflowRepository.update_analysis_status(
            db=db,
            analysis_id=report.analysis_id,
            workflow_status="APPROVED"
        )
        
        # Trigger Notification Agent background task (or internal API trigger) to send email
        background_tasks.add_task(ReportService._trigger_notification_agent, report_id)
        
        return {
            "report_status": "APPROVED",
            "email_status": "SENDING"
        }

    @staticmethod
    def get_pdf(db: Session, user_id: UUID, report_id: UUID) -> str:
        report = ReportRepository.get_report_by_id(db, report_id)
        if not report or not report.analysis or not report.analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
            
        if report.analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
            
        if not report.approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Report must be approved before downloading PDF."
            )
            
        # Return pdf url. Later, we'll return a signed Supabase storage URL.
        # For now, return the stored pdf_url
        if not report.pdf_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF URL not found for this approved report."
            )
        return report.pdf_url

    @staticmethod
    def get_json(db: Session, user_id: UUID, report_id: UUID) -> Dict[str, Any]:
        report = ReportRepository.get_report_by_id(db, report_id)
        if not report or not report.analysis or not report.analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
            
        if report.analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
            
        return report.report_json

    @staticmethod
    async def _trigger_orchestrator_revision(analysis_id: UUID):
        token = "internal_secret_token"
        headers = {"X-Internal-Token": token}
        url = f"{settings.BACKEND_URL}/api/v1/internal/orchestrator/start"
        logger.info(f"Triggering orchestrator for revision on analysis: {analysis_id}")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                await client.post(url, json={"analysis_id": str(analysis_id)}, headers=headers)
        except Exception as e:
            logger.error(f"Error starting revision loop: {str(e)}")

    @staticmethod
    async def _trigger_notification_agent(report_id: UUID):
        token = "internal_secret_token"
        headers = {"X-Internal-Token": token}
        url = f"{settings.BACKEND_URL}/api/v1/internal/agents/notification"
        logger.info(f"Triggering notification agent for report: {report_id}")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                await client.post(url, json={"analysis_id": str(report_id)}, headers=headers) # We pass report_id (which maps to target analysis) or similar internal trigger structure
        except Exception as e:
            logger.error(f"Error calling notification agent: {str(e)}")
