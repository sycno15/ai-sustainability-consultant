from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import settings, logger

app = FastAPI(
    title="AI Sustainability Consultant API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing AI Sustainability Consultant Backend...")

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
            "message": "AI Sustainability Consultant API is running"
        }
    }
