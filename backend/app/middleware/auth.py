import jwt
from jwt import PyJWKClient
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings, logger
from app.utils.db import get_db
from app.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
from uuid import UUID

# We use HTTPBearer to extract the Authorization header
security = HTTPBearer()

# JWKS client for ES256 verification (caches keys automatically)
_jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
_jwks_client = PyJWKClient(_jwks_url, cache_keys=True)

def _decode_token(token: str) -> dict:
    """Decode a Supabase JWT, supporting both HS256 (legacy) and ES256 (current)."""
    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "HS256")

    if alg == "HS256":
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            leeway=60,
        )

    # ES256 — resolve signing key from Supabase JWKS
    signing_key = _jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256"],
        audience="authenticated",
        leeway=60,
    )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = _decode_token(token)
        
        user_id_str = payload.get("sub")
        email = payload.get("email")
        
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token payload is missing user ID (sub)")
            
        user_uuid = UUID(user_id_str)
        
        user = UserRepository.get_user_by_id(db, user_uuid)
        if not user:
            full_name = payload.get("user_metadata", {}).get("full_name", email.split('@')[0])
            user = UserRepository.create_user(db, user_id=user_uuid, email=email, full_name=full_name)
            logger.info(f"User {user_uuid} auto-mirrored locally on auth check.")
            
        return user
        
    except jwt.ExpiredSignatureError as e:
        logger.warning(f"JWT expired: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication token is invalid")
    except Exception as e:
        logger.error(f"Auth middleware unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Let's add a helper method in UserRepository since we called `UserRepository.get_current_user_profile`
# Wait, in user_repository we defined `get_user_by_id`.
# Let's fix that check to use get_user_by_id!
