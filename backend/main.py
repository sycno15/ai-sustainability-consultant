from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, logger

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.assessment import router as assessment_router
from app.api.workflow import router as workflow_router
from app.api.report import router as report_router
from app.api.email import router as email_router
from app.api.internal import router as internal_router

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="AI Sustainability Consultant API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)

# Local/dev origins (LAN IP included so phone/other devices on the network work)
_cors_origins = {
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ai-sustainability-consultant.vercel.app",
}
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_cors_origins),
    allow_origin_regex = (
    r"https://ai-sustainability-consultant\.vercel\.app",
    r"|http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+):\d+",
),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static folder exists for fallback PDF storage
os.makedirs("static/reports", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(assessment_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")
app.include_router(report_router, prefix="/api/v1")
app.include_router(email_router, prefix="/api/v1")
app.include_router(internal_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing AI Sustainability Consultant Backend...")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException on {request.url.path}: {exc.detail} (Status: {exc.status_code})")
    
    code = "BAD_REQUEST"
    if exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        code = "FORBIDDEN"
    elif exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 422:
        code = "VALIDATION_ERROR"
        
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": exc.detail
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        # Clean up path locations (e.g. body -> email)
        loc_parts = [str(p) for p in err.get("loc", []) if p != "body"]
        loc = " -> ".join(loc_parts)
        msg = err.get("msg", "")
        if loc:
            errors.append(f"{loc}: {msg}")
        else:
            errors.append(msg)
            
    message = "; ".join(errors) if errors else "Validation failed"
    logger.warning(f"Validation error on {request.url.path}: {message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred on path {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please check logs."
            }
        }
    )

@app.get("/", tags=["Health"])
async def health_check():
    logger.info("Health check endpoint hit.")
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "message": "AI Sustainability Consultant API is running",
            "port_marker": "backend-8001-v2"
        }
    }
