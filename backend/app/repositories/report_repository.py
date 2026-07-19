from sqlalchemy.orm import Session
from app.models.models import Report, Feedback, BusinessProfile, Analysis
from uuid import UUID
from typing import List, Optional

class ReportRepository:
    @staticmethod
    def get_report_by_id(db: Session, report_id: UUID) -> Optional[Report]:
        return db.query(Report).filter(Report.id == report_id).first()

    @staticmethod
    def get_report_by_analysis_id(db: Session, analysis_id: UUID) -> Optional[Report]:
        return db.query(Report).filter(Report.analysis_id == analysis_id).first()

    @staticmethod
    def get_reports_by_user_id(db: Session, user_id: UUID) -> List[Report]:
        return db.query(Report)\
            .join(Analysis, Report.analysis_id == Analysis.id)\
            .join(BusinessProfile, Analysis.business_id == BusinessProfile.id)\
            .filter(BusinessProfile.user_id == user_id)\
            .order_by(Report.id.desc())\
            .all()

    @staticmethod
    def create_report(
        db: Session,
        analysis_id: UUID,
        report_json: dict,
        overall_score: Optional[float] = None
    ) -> Report:
        # Check if report already exists for this analysis, if so overwrite or update it
        existing = db.query(Report).filter(Report.analysis_id == analysis_id).first()
        if existing:
            existing.report_json = report_json
            existing.overall_score = overall_score
            existing.approved = False
            existing.pdf_url = None
            db.commit()
            db.refresh(existing)
            return existing
            
        report = Report(
            analysis_id=analysis_id,
            report_json=report_json,
            overall_score=overall_score,
            approved=False
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def approve_report(db: Session, report_id: UUID, pdf_url: Optional[str] = None) -> Report:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError(f"Report with ID {report_id} not found")
        report.approved = True
        if pdf_url:
            report.pdf_url = pdf_url
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def create_feedback(db: Session, report_id: UUID, feedback_text: str) -> Feedback:
        feedback = Feedback(
            report_id=report_id,
            feedback=feedback_text
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        return feedback

    @staticmethod
    def get_feedbacks_by_report_id(db: Session, report_id: UUID) -> List[Feedback]:
        return db.query(Feedback).filter(Feedback.report_id == report_id).order_by(Feedback.id.desc()).all()
