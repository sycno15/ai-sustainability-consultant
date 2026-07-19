import httpx
from supabase import create_client, Client, ClientOptions
from app.config import settings, logger
from app.repositories.user_repository import UserRepository
from sqlalchemy.orm import Session
import uuid

class AuthService:
    def __init__(self):
        # We use a custom httpx client to disable HTTP/2 and increase timeout to 60.0s to avoid timeouts
        http_client = httpx.Client(timeout=60.0, http2=False)
        options = ClientOptions(httpx_client=http_client)
        # We use the Service Role Key to bypass RLS for administrative user creation,
        # but the client session JWT is verified for user endpoints.
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
            options=options
        )

    def register(self, email: str, password: str, full_name: str, db: Session):
        logger.info(f"Attempting to register user: {email}")
        try:
            # 1. Create user in Supabase GoTrue Auth and confirm email automatically
            response = self.supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "full_name": full_name
                }
            })
            
            # The response contains the user object.
            user = response.user
            if not user:
                raise Exception("Supabase Auth registration returned an empty user response.")
            
            user_uuid = uuid.UUID(user.id)
            logger.info(f"Supabase Auth user created successfully. User ID: {user_uuid}")

            # 2. Mirror the user profile locally in our PostgreSQL users table
            # Check if user already exists locally (edge case)
            local_user = UserRepository.get_user_by_id(db, user_uuid)
            if not local_user:
                UserRepository.create_user(db, user_id=user_uuid, email=email, full_name=full_name)
                logger.info(f"User profile mirrored locally in database.")
            
            return {"user_id": str(user_uuid)}
            
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            raise e

    def login(self, email: str, password: str):
        logger.info(f"Attempting to login user: {email}")
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            session = response.session
            if not session:
                raise Exception("No active session returned from Supabase Auth.")
                
            return {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "expires_in": session.expires_in
            }
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise e

    def logout(self, token: str):
        logger.info("Attempting to sign out user session...")
        try:
            # GoTrue client requires the user token to perform logout.
            # We initialize a client with the user's specific JWT to sign out.
            http_client = httpx.Client(timeout=60.0, http2=False)
            options = ClientOptions(httpx_client=http_client)
            user_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY, options=options)
            user_client.postgrest.auth(token)
            user_client.auth.sign_out(token)
            logger.info("Session signed out successfully.")
            return True
        except Exception as e:
            logger.error(f"Error during signout: {str(e)}")
            # Even if signout fails on the server, we want to proceed.
            raise e

    def reset_password(self, email: str):
        logger.info(f"Requesting password reset for: {email}")
        try:
            self.supabase.auth.reset_password_for_email(email)
            logger.info(f"Password reset link sent to {email}")
            return True
        except Exception as e:
            logger.error(f"Error requesting password reset: {str(e)}")
            raise e
