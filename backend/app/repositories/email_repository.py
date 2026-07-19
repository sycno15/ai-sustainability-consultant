from sqlalchemy.orm import Session
from app.models.models import EmailLog
from uuid import UUID
from typing import List, Optional

class EmailRepository:
    @staticmethod
    def get_email_log_by_id(db: Session, email_log_id: UUID) -> Optional[EmailLog]:
        return db.query(EmailLog).filter(EmailLog.id == email_log_id).first()

    @staticmethod
    def get_latest_email_log_by_report_id(db: Session, report_id: UUID) -> Optional[EmailLog]:
        return db.query(EmailLog).filter(EmailLog.report_id == report_id).order_by(EmailLog.sent_at.desc()).first()

    @staticmethod
    def get_email_history_by_report_id(db: Session, report_id: UUID) -> List[EmailLog]:
        return db.query(EmailLog).filter(EmailLog.report_id == report_id).order_by(EmailLog.sent_at.desc()).all()

    @staticmethod
    def create_email_log(
        db: Session,
        report_id: UUID,
        recipient: str,
        delivery_status: str
    ) -> EmailLog:
        email_log = EmailLog(
            report_id=report_id,
            recipient=recipient,
            delivery_status=delivery_status
        )
        db.add(email_log)
        db.commit()
        db.refresh(email_log)
        return email_log

    @staticmethod
    def update_email_status(
        db: Session,
        email_log_id: UUID,
        status: str
    ) -> EmailLog:
        email_log = db.query(EmailLog).filter(EmailLog.id == email_log_id).first()
        if not email_log:
            raise ValueError(f"Email log with ID {email_log_id} not found")
        email_log.delivery_status = status
        db.commit()
        db.refresh(email_log)
        return email_log
