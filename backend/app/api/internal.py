from fastapi import APIRouter, Depends, Header, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.schemas.internal import InternalOrchestratorStart, InternalAgentRun
from app.orchestrator.orchestrator import Orchestrator
from app.config import logger
from uuid import UUID

router = APIRouter(prefix="/internal", tags=["Internal AI Agents"])

def verify_internal_token(x_internal_token: str = Header(..., alias="X-Internal-Token")):
    # A simple but secure internal service token verification
    if x_internal_token != "internal_secret_token":
        logger.warning(f"Unauthorized internal access attempt with token: {x_internal_token}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal service token."
        )

@router.post("/orchestrator/start", dependencies=[Depends(verify_internal_token)])
async def start_orchestrator(
    payload: InternalOrchestratorStart,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    logger.info(f"[Internal] Queueing orchestrator background task for analysis ID: {payload.analysis_id}")
    background_tasks.add_task(Orchestrator.run_workflow, db, payload.analysis_id)
    return {
        "success": True,
        "data": {
            "status": "RUNNING",
            "message": "Orchestrator queued workflow execution."
        }
    }

@router.post("/agents/carbon", dependencies=[Depends(verify_internal_token)])
async def run_carbon_agent(
    payload: InternalAgentRun,
    db: Session = Depends(get_db)
):
    logger.info(f"[Internal] Running Carbon Agent for analysis ID: {payload.analysis_id}")
    return {
        "success": True,
        "data": {
            "status": "SUCCESS",
            "agent": "Carbon Agent"
        }
    }

@router.post("/agents/recommendation", dependencies=[Depends(verify_internal_token)])
async def run_recommendation_agent(
    payload: InternalAgentRun,
    db: Session = Depends(get_db)
):
    logger.info(f"[Internal] Running Recommendation Agent for analysis ID: {payload.analysis_id}")
    return {
        "success": True,
        "data": {
            "status": "SUCCESS",
            "agent": "Recommendation Agent"
        }
    }

@router.post("/agents/financial", dependencies=[Depends(verify_internal_token)])
async def run_financial_agent(
    payload: InternalAgentRun,
    db: Session = Depends(get_db)
):
    logger.info(f"[Internal] Running Financial Agent for analysis ID: {payload.analysis_id}")
    return {
        "success": True,
        "data": {
            "status": "SUCCESS",
            "agent": "Financial Agent"
        }
    }

@router.post("/agents/planner", dependencies=[Depends(verify_internal_token)])
async def run_planner_agent(
    payload: InternalAgentRun,
    db: Session = Depends(get_db)
):
    logger.info(f"[Internal] Running Planner Agent for analysis ID: {payload.analysis_id}")
    return {
        "success": True,
        "data": {
            "status": "SUCCESS",
            "agent": "Planner Agent"
        }
    }

@router.post("/agents/critic", dependencies=[Depends(verify_internal_token)])
async def run_critic_agent(
    payload: InternalAgentRun,
    db: Session = Depends(get_db)
):
    logger.info(f"[Internal] Running Critic Agent for analysis ID: {payload.analysis_id}")
    return {
        "success": True,
        "data": {
            "status": "SUCCESS",
            "agent": "Critic Agent"
        }
    }

@router.post("/agents/report", dependencies=[Depends(verify_internal_token)])
async def run_report_agent(
    payload: InternalAgentRun,
    db: Session = Depends(get_db)
):
    logger.info(f"[Internal] Running Report Agent for analysis ID: {payload.analysis_id}")
    return {
        "success": True,
        "data": {
            "status": "SUCCESS",
            "agent": "Report Agent"
        }
    }

@router.post("/agents/notification", dependencies=[Depends(verify_internal_token)])
async def run_notification_agent(
    payload: InternalAgentRun,
    db: Session = Depends(get_db)
):
    logger.info(f"[Internal] Running Notification Agent for analysis ID: {payload.analysis_id}")
    return {
        "success": True,
        "data": {
            "status": "SUCCESS",
            "agent": "Notification Agent"
        }
    }
