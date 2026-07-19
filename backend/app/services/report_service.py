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
        
        # Trigger background orchestrator to process revision feedback directly
        background_tasks.add_task(ReportService._run_orchestrator_revision_bg, report.analysis_id)
        
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
        ReportRepository.approve_report(db, report_id, None)
        
        # Update workflow/analysis status to APPROVED
        WorkflowRepository.update_analysis_status(
            db=db,
            analysis_id=report.analysis_id,
            workflow_status="APPROVED"
        )
        
        # Trigger PDF generation + Storage upload + Email dispatch background task directly
        background_tasks.add_task(ReportService._run_notification_flow, report_id)
        
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
    async def _run_orchestrator_revision_bg(analysis_id: UUID):
        from app.orchestrator.orchestrator import Orchestrator
        from app.utils.db import SessionLocal
        logger.info(f"Triggering background orchestrator directly for revision on analysis: {analysis_id}")
        db = SessionLocal()
        try:
            await Orchestrator.run_workflow(db, analysis_id)
        except Exception as e:
            logger.error(f"Error running revision orchestrator directly: {str(e)}")
        finally:
            db.close()

    @staticmethod
    async def _run_notification_flow(report_id: UUID):
        from app.utils.db import SessionLocal
        from app.services.pdf_service import PDFService
        from app.services.storage_service import StorageService
        from app.services.email_service import EmailService
        
        logger.info(f"Running notification flow (PDF gen + Email dispatch) for Report ID: {report_id}")
        db = SessionLocal()
        try:
            report = ReportRepository.get_report_by_id(db, report_id)
            if not report or not report.analysis or not report.analysis.business:
                logger.error(f"Report {report_id} not found in database.")
                return
                
            # 1. Generate PDF Report Bytes
            logger.info("Generating Report PDF bytes...")
            overall_score = float(report.overall_score) if report.overall_score is not None else 95.0
            pdf_bytes = PDFService.generate_pdf(report.report_json, overall_score)
            
            # 2. Upload PDF Report
            logger.info("Uploading PDF to Storage...")
            pdf_filename = f"report_{report_id}.pdf"
            pdf_url = StorageService.upload_pdf(pdf_bytes, pdf_filename)
            
            # 3. Update Report PDF URL
            report.pdf_url = pdf_url
            db.commit()
            
            # 4. Dispatch Email with Report Link
            recipient_email = report.analysis.business.user.email
            logger.info(f"Dispatching report email to: {recipient_email}")
            await EmailService.send_report_email(db, report_id, recipient_email)
            
            logger.info(f"Notification flow completed successfully for Report ID: {report_id}")
        except Exception as e:
            logger.error(f"Error during notification flow: {str(e)}")
        finally:
            db.close()
