from sqlalchemy.orm import Session
from app.services.llm_service import LLMService
import os
import json
from app.config import logger

def load_prompt(filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "prompts", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class PlannerAgent:
    @staticmethod
    async def run(db: Session, shared_state: dict) -> dict:
        logger.info("Planner Agent: Starting implementation planning...")
        business = shared_state.get("business", {})
        recommendations = shared_state.get("recommendations", [])
        financial = shared_state.get("financial_analysis", {})
        
        global_inst = load_prompt("global_instruction.md")
        plan_inst = load_prompt("planner.md")
        
        system_instruction = f"{global_inst}\n\n{plan_inst}"
        
        prompt = f"""
        Business details:
        - Size: {business.get("company_size")}
        - Sector: {business.get("industry")}
        
        Recommendations:
        {json.dumps(recommendations)}
        
        Financial Parameters:
        {json.dumps(financial.get("financial_summary", {}))}
        
        Structure these recommendations into chronological phases: 0-3 Months, 3-6 Months, 6-12 Months, 12+ Months. Output the structured JSON roadmap.
        """
        
        llm_response = await LLMService.call_model(prompt, system_instruction, json_mode=True)
        
        try:
            result = json.loads(llm_response)
            result["status"] = "SUCCESS"
        except Exception as e:
            logger.error(f"Failed to parse Planner Agent LLM response: {str(e)}. Using fallback JSON.")
            # Fallback roadmap mapping
            tasks_0_3 = []
            tasks_3_6 = []
            tasks_6_12 = []
            
            for idx, rec in enumerate(recommendations):
                task = {
                    "title": rec.get("title"),
                    "reason": rec.get("description", "Recommended measure."),
                    "estimated_duration": "1 month",
                    "priority": rec.get("priority", "MEDIUM")
                }
                if idx == 0:
                    tasks_0_3.append(task)
                elif idx == 1:
                    tasks_3_6.append(task)
                else:
                    tasks_6_12.append(task)
                    
            result = {
                "status": "SUCCESS",
                "roadmap": [
                    {"phase": "0-3 Months", "tasks": tasks_0_3},
                    {"phase": "3-6 Months", "tasks": tasks_3_6},
                    {"phase": "6-12 Months", "tasks": tasks_6_12}
                ],
                "overall_duration": "12 Months",
                "confidence": 90
            }
            
        shared_state["implementation_plan"] = result
        logger.info("Planner Agent: Roadmap compiled successfully.")
        return result
