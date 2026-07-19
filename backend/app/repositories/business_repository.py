from sqlalchemy.orm import Session
from app.models.models import BusinessProfile, BusinessMetric, Industry
from uuid import UUID
from typing import List, Optional

class BusinessRepository:
    @staticmethod
    def get_profile_by_id(db: Session, profile_id: UUID) -> Optional[BusinessProfile]:
        return db.query(BusinessProfile).filter(BusinessProfile.id == profile_id).first()

    @staticmethod
    def get_profiles_by_user_id(db: Session, user_id: UUID) -> List[BusinessProfile]:
        return db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).all()

    @staticmethod
    def create_profile(
        db: Session,
        user_id: UUID,
        business_name: str,
        industry: str,
        company_size: str,
        description: Optional[str] = None
    ) -> BusinessProfile:
        profile = BusinessProfile(
            user_id=user_id,
            business_name=business_name,
            industry=industry,
            company_size=company_size,
            description=description
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def create_metrics(
        db: Session,
        business_id: UUID,
        electricity_usage: float,
        diesel_usage: float,
        petrol_usage: float,
        water_usage: float,
        waste_generated: float,
        annual_revenue: float,
        sustainability_budget: float
    ) -> BusinessMetric:
        metrics = BusinessMetric(
            business_id=business_id,
            electricity_usage=electricity_usage,
            diesel_usage=diesel_usage,
            petrol_usage=petrol_usage,
            water_usage=water_usage,
            waste_generated=waste_generated,
            annual_revenue=annual_revenue,
            sustainability_budget=sustainability_budget
        )
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def get_metrics_by_business_id(db: Session, business_id: UUID) -> Optional[BusinessMetric]:
        return db.query(BusinessMetric).filter(BusinessMetric.business_id == business_id).first()

    @staticmethod
    def industry_exists(db: Session, name: str) -> bool:
        # Case-insensitive comparison
        return db.query(Industry).filter(Industry.name.ilike(name)).first() is not None

    @staticmethod
    def delete_profile(db: Session, profile: BusinessProfile) -> None:
        db.delete(profile)
        db.commit()
