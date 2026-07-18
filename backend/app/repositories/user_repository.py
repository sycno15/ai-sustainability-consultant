from sqlalchemy.orm import Session
from app.models.models import User
from uuid import UUID

class UserRepository:
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> User:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, user_id: UUID, email: str, full_name: str) -> User:
        db_user = User(id=user_id, email=email, full_name=full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
