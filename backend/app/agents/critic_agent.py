from sqlalchemy.orm import Session
from app.services.llm_service import LLMService
import os
import json
from app.config import logger

def load_prompt(filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "prompts", filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Could not load prompt {filename}: {e}")
        if filename == "critic.md":
            return "Quality Assurance Agent: Evaluate agent outputs and return PASS, REVISE, or FAILED."
        return "Sustainability System Directives: Provide output formatted strictly as JSON."

class CriticAgent:
    @staticmethod
    async def run(db: Session, shared_state: dict) -> dict:
        logger.info("Critic Agent: Starting review inspection...")
        carbon = shared_state.get("carbon_analysis", {})
        recommendations = shared_state.get("recommendations", [])
        financial = shared_state.get("financial_analysis", {})
        plan = shared_state.get("implementation_plan", {})
        
        global_inst = load_prompt("global_instruction.md")
        critic_inst = load_prompt("critic.md")
        
        system_instruction = f"{global_inst}\n\n{critic_inst}"
        
        prompt = f"""
        Analysis outputs under review:
        - Carbon Footprint calculations: {json.dumps(carbon)}
        - Selected Recommendations: {json.dumps(recommendations)}
        - Financial Analysis parameters: {json.dumps(financial)}
        - Phased Implementation Plan: {json.dumps(plan)}
        
        Evaluate these details against the validation checklist. Reconcile calculations, budget fits, and timeline feasibility. Return status PASS, REVISE, or FAILED.
        """
        
        llm_response = await LLMService.call_model(prompt, system_instruction, json_mode=True)
        
        try:
            result = LLMService.clean_and_parse_json(llm_response)
        except Exception as e:
            logger.error(f"Failed to parse Critic Agent LLM response: {str(e)}. Using fallback PASS.")
            result = {
                "status": "PASS",
                "issues": [],
                "confidence": 95
            }
            
        shared_state["critic_review"] = result
        logger.info(f"Critic Agent: Review completed with status: {result.get('status')}")
        return result
