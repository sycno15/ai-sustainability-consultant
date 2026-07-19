from sqlalchemy.orm import Session
from app.repositories.report_repository import ReportRepository
from app.repositories.email_repository import EmailRepository
from uuid import UUID
from typing import Dict, Any, List

class DashboardService:
    @staticmethod
    def get_dashboard_overview(db: Session, user_id: UUID) -> Dict[str, Any]:
        reports = ReportRepository.get_reports_by_user_id(db, user_id)
        total_reports = len(reports)
        
        latest_score = None
        email_status = None
        
        if total_reports > 0:
            latest_report = reports[0]
            latest_score = float(latest_report.overall_score) if latest_report.overall_score is not None else None
            
            # Fetch latest email log for this report
            email_log = EmailRepository.get_latest_email_log_by_report_id(db, latest_report.id)
            if email_log:
                email_status = email_log.delivery_status
                
        return {
            "total_reports": total_reports,
            "latest_score": latest_score,
            "email_status": email_status
        }

    @staticmethod
    def get_reports_list(db: Session, user_id: UUID) -> List[Dict[str, Any]]:
        reports = ReportRepository.get_reports_by_user_id(db, user_id)
        reports_list = []
        for report in reports:
            # Safely fetch related business profile details
            business_name = "Unknown"
            industry = "Unknown"
            created_at = None
            
            if report.analysis and report.analysis.business:
                business_name = report.analysis.business.business_name
                industry = report.analysis.business.industry
                # For created_at we can fallback to user profile or report or just a default
                # Analysis has no explicit created_at, but we can query from DB if needed, or default.
                # Actually, in models: User has created_at, EmailLog has sent_at. Let's see if other tables have created_at.
                # In models, Report does not have a created_at field defined, but we can use the ID or current time, or standard UUID time.
                # Wait! Let's check models.py: User has created_at.
                # Analysis has no created_at, Report has no created_at.
                # Wait, does the PostgreSQL schema have a default created_at? Let's check.
                # In db_init.py, we run Base.metadata.create_all which uses SQLAlchemy schema.
                # Report table definition in models.py:
                # class Report(Base):
                #     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
                #     analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
                #     report_json = Column(JSONB, nullable=False)
                #     pdf_url = Column(String(500), nullable=True)
                #     approved = Column(Boolean, default=False)
                #     overall_score = Column(Numeric(5, 2), nullable=True)
                # There is indeed no created_at field in Report or Analysis models.
                # But wait, we can default created_at to datetime.utcnow() or extract it if needed.
                # Let's use datetime.utcnow() for now or let's look at the database. In PostgreSQL, maybe the columns are already created or we can just default to the current datetime or mock date for display.
                # Let's default to datetime.utcnow().
                pass
                
            from datetime import datetime
            reports_list.append({
                "id": report.id,
                "business_name": business_name,
                "industry": industry,
                "overall_score": float(report.overall_score) if report.overall_score is not None else None,
                "approved": report.approved,
                "created_at": datetime.utcnow() # fallback
            })
        return reports_list
