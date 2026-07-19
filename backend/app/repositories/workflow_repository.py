from sqlalchemy.orm import Session
from app.models.models import Analysis, ToolLog
from uuid import UUID
from typing import List, Optional

class WorkflowRepository:
    @staticmethod
    def get_analysis_by_id(db: Session, analysis_id: UUID) -> Optional[Analysis]:
        return db.query(Analysis).filter(Analysis.id == analysis_id).first()

    @staticmethod
    def get_analysis_by_business_id(db: Session, business_id: UUID) -> Optional[Analysis]:
        return db.query(Analysis).filter(Analysis.business_id == business_id).order_by(Analysis.id.desc()).first()

    @staticmethod
    def create_analysis(db: Session, business_id: UUID) -> Analysis:
        analysis = Analysis(
            business_id=business_id,
            workflow_status="Draft",
            retry_count=0,
            shared_state={}
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def update_analysis_status(
        db: Session,
        analysis_id: UUID,
        workflow_status: str,
        current_agent: Optional[str] = None,
        retry_count: Optional[int] = None,
        shared_state: Optional[dict] = None
    ) -> Analysis:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found")
        
        analysis.workflow_status = workflow_status
        if current_agent is not None:
            analysis.current_agent = current_agent
        if retry_count is not None:
            analysis.retry_count = retry_count
        if shared_state is not None:
            analysis.shared_state = shared_state
            
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def create_tool_log(
        db: Session,
        analysis_id: UUID,
        agent: str,
        tool: str,
        duration: float,
        status: str
    ) -> ToolLog:
        tool_log = ToolLog(
            analysis_id=analysis_id,
            agent=agent,
            tool=tool,
            duration=duration,
            status=status
        )
        db.add(tool_log)
        db.commit()
        db.refresh(tool_log)
        return tool_log

    @staticmethod
    def get_tool_logs_by_analysis_id(db: Session, analysis_id: UUID) -> List[ToolLog]:
        return db.query(ToolLog).filter(ToolLog.analysis_id == analysis_id).order_by(ToolLog.id.asc()).all()
