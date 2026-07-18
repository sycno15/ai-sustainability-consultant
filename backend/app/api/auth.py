from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.schemas.auth import UserRegister, UserLogin, ResetPassword, TokenData, UserProfile
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: Session = Depends(get_db)):
    try:
        data = auth_service.register(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            db=db
        )
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        # Standard error response format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login")
async def login(payload: UserLogin):
    try:
        data = auth_service.login(
            email=payload.email,
            password=payload.password
        )
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # Since we validate JWT locally, the client deletes the token from its storage.
    # We can also call Supabase to sign out the session if we pass the access token.
    # For compliance with API specs:
    return {
        "success": True
    }

@router.post("/reset-password")
async def reset_password(payload: ResetPassword):
    try:
        auth_service.reset_password(email=payload.email)
        return {
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/profile", response_model=None)
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name
        }
    }
