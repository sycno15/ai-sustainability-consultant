from app.config import settings, logger
from supabase import create_client, Client
import os

class StorageService:
    _supabase: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._supabase is not None:
            return cls._supabase
            
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_ANON_KEY
        
        if not url or not key or "mock" in url.lower() or "mock" in key.lower():
            return None
            
        try:
            cls._supabase = create_client(url, key)
            return cls._supabase
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {str(e)}")
            return None

    @classmethod
    def upload_pdf(cls, pdf_bytes: bytes, file_name: str) -> str:
        # 1. Try Supabase Storage first
        client = cls.get_client()
        if client is not None:
            try:
                # Upload bytes to bucket "reports"
                # If file already exists, this might raise an error; we swallow it and overwrite or check.
                client.storage.from_("reports").upload(
                    path=file_name,
                    file=pdf_bytes,
                    file_options={"content-type": "application/pdf", "x-upsert": "true"}
                )
                public_url = client.storage.from_("reports").get_public_url(file_name)
                logger.info(f"Report PDF uploaded successfully to Supabase Storage: {public_url}")
                return public_url
            except Exception as e:
                logger.warning(f"Supabase storage upload failed: {str(e)}. Falling back to local static storage.")

        # 2. Local fallback storage
        logger.info(f"Using local static storage for report PDF: {file_name}")
        os.makedirs("static/reports", exist_ok=True)
        local_path = os.path.join("static/reports", file_name)
        with open(local_path, "wb") as f:
            f.write(pdf_bytes)
            
        backend_url = settings.BACKEND_URL.rstrip("/")
        return f"{backend_url}/static/reports/{file_name}"
