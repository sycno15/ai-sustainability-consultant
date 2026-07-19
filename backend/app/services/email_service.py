from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.email_repository import EmailRepository
from app.repositories.report_repository import ReportRepository
from uuid import UUID
from typing import Dict, Any
from app.config import settings, logger
import httpx
from datetime import datetime

class EmailService:
    @staticmethod
    def get_email_status(db: Session, user_id: UUID, report_id: UUID) -> Dict[str, Any]:
        report = ReportRepository.get_report_by_id(db, report_id)
        if not report or not report.analysis or not report.analysis.business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
            
        if report.analysis.business.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this report's email status"
            )
            
        email_log = EmailRepository.get_latest_email_log_by_report_id(db, report_id)
        if not email_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No email has been sent for this report yet."
            )
            
        return {
            "status": email_log.delivery_status,
            "recipient": email_log.recipient,
            "sent_at": email_log.sent_at
        }

    @staticmethod
    async def send_report_email(db: Session, report_id: UUID, recipient: str) -> Dict[str, Any]:
        logger.info(f"Preparing to send report email for report {report_id} to {recipient}")
        
        # 1. Prevent duplicate email sending
        existing_log = EmailRepository.get_latest_email_log_by_report_id(db, report_id)
        if existing_log and existing_log.delivery_status == "DELIVERED":
            logger.info("Email already delivered for this report. Skipping.")
            return {"delivery_status": "DELIVERED"}
            
        report = ReportRepository.get_report_by_id(db, report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
            
        # Get recipient name
        recipient_name = "Business Owner"
        if report.analysis and report.analysis.business and report.analysis.business.user:
            recipient_name = report.analysis.business.user.full_name or recipient_name

        # Prepare email content
        subject = "Your Sustainability Assessment Report is Ready"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #2e7d32;">Hello {recipient_name},</h2>
                <p>Thank you for using AI Sustainability Consultant.</p>
                <p>Your sustainability assessment has been completed successfully.</p>
                <p>The report includes:</p>
                <ul>
                    <li>Carbon footprint assessment</li>
                    <li>Sustainability recommendations</li>
                    <li>Financial ROI analysis</li>
                    <li>Implementation roadmap</li>
                    <li>SDG alignment</li>
                </ul>
                <p>You can view and download the PDF report here:<br>
                <a href="{report.pdf_url or '#'}" style="display: inline-block; padding: 10px 20px; margin: 10px 0; background-color: #2e7d32; color: #fff; text-decoration: none; border-radius: 3px;">
                    View PDF Report
                </a></p>
                <p>We hope this report helps your organization make informed sustainability decisions.</p>
                <br>
                <p>Best regards,<br>
                <strong>AI Sustainability Consultant Team</strong></p>
            </div>
        </body>
        </html>
        """
        
        # 2. Resend API call (with mock fallback for local testing)
        api_key = settings.RESEND_API_KEY
        delivery_status = "FAILED"
        
        if not api_key or "mock" in api_key.lower():
            logger.info("Using mock Resend integration (local/bootstrap testing). Email marked as DELIVERED.")
            delivery_status = "DELIVERED"
        else:
            try:
                # Actual Resend call
                url = "https://api.resend.com/emails"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "from": "AI Sustainability Consultant <onboarding@resend.dev>",
                    "to": [recipient],
                    "subject": subject,
                    "html": html_content
                }
                
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    if response.status_code in [200, 201]:
                        delivery_status = "DELIVERED"
                        logger.info("Email delivered successfully via Resend API.")
                    else:
                        logger.error(f"Resend API error: {response.status_code} - {response.text}")
                        delivery_status = "FAILED"
            except Exception as e:
                logger.error(f"Failed to communicate with Resend API: {str(e)}")
                delivery_status = "FAILED"
                
        # 3. Create log
        EmailRepository.create_email_log(
            db=db,
            report_id=report_id,
            recipient=recipient,
            delivery_status=delivery_status
        )
        
        return {"delivery_status": delivery_status}
