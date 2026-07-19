from sqlalchemy.orm import Session
from uuid import UUID
import time
from app.config import logger
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.report_repository import ReportRepository

# Import individual Agent modules
from app.agents.carbon_agent import CarbonAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.financial_agent import FinancialAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.critic_agent import CriticAgent
from app.agents.report_agent import ReportAgent

class Orchestrator:
    @staticmethod
    async def run_workflow(db: Session, analysis_id: UUID) -> None:
        logger.info(f"Orchestrator: Initiating workflow execution for Analysis ID {analysis_id}")
        
        # 1. Fetch analysis record
        analysis = WorkflowRepository.get_analysis_by_id(db, analysis_id)
        if not analysis or not analysis.business:
            logger.error(f"Orchestrator: Analysis ID {analysis_id} not found in database.")
            return
            
        profile = analysis.business
        metrics = profile.metrics[0] if profile.metrics else None
        
        if not metrics:
            logger.error(f"Orchestrator: Metrics missing for Business Profile {profile.id}.")
            WorkflowRepository.update_analysis_status(
                db=db,
                analysis_id=analysis_id,
                workflow_status="FAILED"
            )
            return

        # 2. Build initial shared context state
        shared_state = {
            "business": {
                "id": str(profile.id),
                "business_name": profile.business_name,
                "industry": profile.industry,
                "company_size": profile.company_size,
                "description": profile.description
            },
            "metrics": {
                "electricity_usage": float(metrics.electricity_usage),
                "diesel_usage": float(metrics.diesel_usage),
                "petrol_usage": float(metrics.petrol_usage),
                "water_usage": float(metrics.water_usage),
                "waste_generated": float(metrics.waste_generated),
                "annual_revenue": float(metrics.annual_revenue),
                "sustainability_budget": float(metrics.sustainability_budget)
            },
            "carbon_analysis": {},
            "recommendations": [],
            "financial_analysis": {},
            "implementation_plan": {},
            "critic_review": {},
            "report": {},
            "metadata": {}
        }
        
        # Initialize execution tracking variables
        retry_count = 0
        max_replans = 2
        
        agent_steps = [
            ("Carbon Agent", CarbonAgent.run),
            ("Recommendation Agent", RecommendationAgent.run),
            ("Financial Agent", FinancialAgent.run),
            ("Planner Agent", PlannerAgent.run),
            ("Critic Agent", CriticAgent.run)
        ]
        
        step_idx = 0
        
        while step_idx < len(agent_steps):
            agent_name, agent_run_fn = agent_steps[step_idx]
            logger.info(f"Orchestrator: Running {agent_name}...")
            
            # Update analysis tracking status
            WorkflowRepository.update_analysis_status(
                db=db,
                analysis_id=analysis_id,
                workflow_status="RUNNING",
                current_agent=agent_name,
                retry_count=retry_count,
                shared_state=shared_state
            )
            
            # Execute agent and measure execution duration
            start_time = time.time()
            status = "Success"
            try:
                await agent_run_fn(db, shared_state)
            except Exception as e:
                logger.error(f"Orchestrator: Error running {agent_name}: {str(e)}")
                status = "Failed"
                
            end_time = time.time()
            duration = end_time - start_time
            
            # Save duration and status to tool_logs
            WorkflowRepository.create_tool_log(
                db=db,
                analysis_id=analysis_id,
                agent=agent_name,
                tool="LLM Call / DB Tool",
                duration=duration,
                status=status
            )
            
            if status == "Failed":
                # Mark workflow failed on agent error crash
                logger.error(f"Orchestrator: Core agent execution failed at {agent_name}. Stopping.")
                WorkflowRepository.update_analysis_status(
                    db=db,
                    analysis_id=analysis_id,
                    workflow_status="FAILED"
                )
                return
                
            # If Critic completes, evaluate approval PASS/REVISE review loops
            if agent_name == "Critic Agent":
                critic_review = shared_state.get("critic_review", {})
                critic_status = critic_review.get("status", "PASS").upper()
                
                if critic_status == "PASS":
                    logger.info("Orchestrator: Critic review PASSED. Proceeding to report writing.")
                    
                    # Run Report Writer Agent
                    logger.info("Orchestrator: Running Report Agent...")
                    WorkflowRepository.update_analysis_status(
                        db=db,
                        analysis_id=analysis_id,
                        workflow_status="RUNNING",
                        current_agent="Report Agent"
                    )
                    
                    start_time = time.time()
                    report_status = "Success"
                    try:
                        await ReportAgent.run(db, shared_state)
                    except Exception as e:
                        logger.error(f"Orchestrator: Report Agent compile error: {str(e)}")
                        report_status = "Failed"
                    duration = time.time() - start_time
                    
                    WorkflowRepository.create_tool_log(
                        db=db,
                        analysis_id=analysis_id,
                        agent="Report Agent",
                        tool="LLM Report Synthesis",
                        duration=duration,
                        status=report_status
                    )
                    
                    if report_status == "Failed":
                        WorkflowRepository.update_analysis_status(db=db, analysis_id=analysis_id, workflow_status="FAILED")
                        return
                        
                    # Save final report to DB reports table
                    report_data = shared_state.get("report", {})
                    overall_score = shared_state.get("critic_review", {}).get("confidence", 95.0)
                    
                    ReportRepository.create_report(
                        db=db,
                        analysis_id=analysis_id,
                        report_json=report_data,
                        overall_score=overall_score
                    )
                    
                    # Mark workflow complete
                    WorkflowRepository.update_analysis_status(
                        db=db,
                        analysis_id=analysis_id,
                        workflow_status="COMPLETED",
                        current_agent="Report Agent",
                        shared_state=shared_state
                    )
                    logger.info(f"Orchestrator: Analysis ID {analysis_id} workflow COMPLETED successfully.")
                    return
                    
                elif critic_status == "REVISE":
                    responsible_agent = critic_review.get("responsible_agent", "Recommendation Agent")
                    logger.warning(f"Orchestrator: Critic review flagged REVISE. Responsible: {responsible_agent}.")
                    
                    if retry_count >= max_replans:
                        logger.error("Orchestrator: Maximum Critic replanning attempts reached. Failing workflow.")
                        WorkflowRepository.update_analysis_status(
                            db=db,
                            analysis_id=analysis_id,
                            workflow_status="FAILED"
                        )
                        return
                        
                    retry_count += 1
                    
                    # Resolve step index matching target responsible agent
                    matched_idx = next(
                        (i for i, step in enumerate(agent_steps) if step[0] == responsible_agent), 
                        2 # Default back to Financial Agent if not resolved
                    )
                    
                    # Backtrack step index pointer
                    step_idx = matched_idx
                    logger.info(f"Orchestrator: Backtracking execution pointer to Step {step_idx}: {responsible_agent}.")
                    continue # Bypass step_idx increment
                    
                else:
                    # Treat critic FAILED as global failure
                    logger.error("Orchestrator: Critic review flagged FAILED. Stopping.")
                    WorkflowRepository.update_analysis_status(
                        db=db,
                        analysis_id=analysis_id,
                        workflow_status="FAILED"
                    )
                    return
            
            step_idx += 1
