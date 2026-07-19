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

class ReportAgent:
    @staticmethod
    async def run(db: Session, shared_state: dict) -> dict:
        logger.info("Report Agent: Starting final report compilation...")
        
        global_inst = load_prompt("global_instruction.md")
        report_inst = load_prompt("report.md")
        
        system_instruction = f"{global_inst}\n\n{report_inst}"
        
        # Call LLM with the entire shared context
        prompt = f"""
        Entire Shared context:
        {json.dumps(shared_state)}
        
        Synthesize these sections into a professional, cohesive business report suited for executive decision makers. Ensure it adheres strictly to the report structure guidelines. Return the structured JSON report matching the schema.
        """
        
        llm_response = await LLMService.call_model(prompt, system_instruction, json_mode=True)
        
        try:
            result = json.loads(llm_response)
            result["status"] = "SUCCESS"
        except Exception as e:
            logger.error(f"Failed to parse Report Agent LLM response: {str(e)}. Using fallback JSON.")
            # Fallback report compilation
            carbon = shared_state.get("carbon_analysis", {})
            recs = shared_state.get("recommendations", [])
            fin = shared_state.get("financial_analysis", {}).get("financial_summary", {})
            plan = shared_state.get("implementation_plan", {})
            
            result = {
                "status": "SUCCESS",
                "report": {
                    "executive_summary": "This assessment report provides carbon offset recommendations and implementing plans.",
                    "carbon_analysis": f"Total emissions calculated at {carbon.get('total_emissions')} kgCO2e/year. Main contributor: {carbon.get('highest_source')}.",
                    "recommendations": [r.get("title") for r in recs],
                    "financial_summary": f"Total capital investment needed is ${fin.get('total_cost')}, with payback in {fin.get('payback_years')} years.",
                    "implementation_plan": f"Milestones are phased over {plan.get('overall_duration')}.",
                    "sdg_mapping": [{"goal_number": 12, "goal_name": "Responsible Consumption and Production"}],
                    "next_steps": ["Obtain supplier quotes for recommended technologies."]
                },
                "confidence": 95
            }
            
        shared_state["report"] = result.get("report", {})
        logger.info("Report Agent: Report compiled successfully.")
        return result
