from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.repositories.workflow_repository import WorkflowRepository
from uuid import UUID
from typing import Dict, Any, List
import requests
import httpx
from app.config import settings, logger

class WorkflowService:
    @staticmethod
    def get_workflow_status(db: Session, user_id: UUID, analysis_id: UUID) -> Dict[str, Any]:
        analysis = WorkflowRepository.get_analysis_by_id(db, analysis_id)
        if not analysis or not analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow analysis not found"
            )
            
        if analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this workflow"
            )
            
        # Calculate progress estimation based on current_agent or workflow_status
        progress = 0
        status_str = analysis.workflow_status
        
        if status_str == "Draft":
            progress = 0
        elif status_str == "COMPLETED":
            progress = 100
        elif status_str == "FAILED":
            progress = 100
        elif status_str == "RUNNING":
            agent_progress_map = {
                "Carbon Agent": 15,
                "Recommendation Agent": 35,
                "Financial Agent": 55,
                "Planner Agent": 75,
                "Critic Agent": 90,
                "Report Agent": 95
            }
            progress = agent_progress_map.get(analysis.current_agent, 10)
        else:
            progress = 10
            
        report_id = None
        if status_str in ("COMPLETED", "APPROVED"):
            from app.repositories.report_repository import ReportRepository
            report = ReportRepository.get_report_by_analysis_id(db, analysis_id)
            if report:
                report_id = str(report.id)

        return {
            "status": status_str,
            "current_agent": analysis.current_agent,
            "progress": progress,
            "retry_count": analysis.retry_count,
            "report_id": report_id,
        }

    @staticmethod
    def get_timeline(db: Session, user_id: UUID, analysis_id: UUID) -> List[Dict[str, Any]]:
        analysis = WorkflowRepository.get_analysis_by_id(db, analysis_id)
        if not analysis or not analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow analysis not found"
            )
            
        if analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this timeline"
            )
            
        tool_logs = WorkflowRepository.get_tool_logs_by_analysis_id(db, analysis_id)
        timeline = []
        for log in tool_logs:
            timeline.append({
                "agent": log.agent,
                "tool": log.tool,
                "duration": float(log.duration),
                "status": log.status
            })
        return timeline

    @staticmethod
    def start_analysis(
        db: Session,
        user_id: UUID,
        analysis_id: UUID,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        analysis = WorkflowRepository.get_analysis_by_id(db, analysis_id)
        if not analysis or not analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow analysis not found"
            )
            
        if analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
            
        if analysis.workflow_status in ["RUNNING", "COMPLETED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow cannot start twice. It is already running or completed."
            )
            
        # Update status to RUNNING
        WorkflowRepository.update_analysis_status(
            db=db,
            analysis_id=analysis_id,
            workflow_status="RUNNING",
            current_agent="Carbon Agent",
            retry_count=0
        )
        
        # Trigger internal orchestrator asynchronously
        background_tasks.add_task(WorkflowService._run_orchestrator_bg, analysis_id)
        
        return {
            "status": "RUNNING"
        }

    @staticmethod
    async def _run_orchestrator_bg(analysis_id: UUID):
        from app.orchestrator.orchestrator import Orchestrator
        from app.utils.db import SessionLocal
        
        logger.info(f"Triggering background orchestrator directly for analysis: {analysis_id}")
        db = SessionLocal()
        try:
            await Orchestrator.run_workflow(db, analysis_id)
        except Exception as e:
            logger.error(f"Error running orchestrator directly: {str(e)}")
        finally:
            db.close()
