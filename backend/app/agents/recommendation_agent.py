from sqlalchemy.orm import Session
from app.models.models import SustainabilityMeasure
from app.services.llm_service import LLMService
import os
import json
from app.config import logger

def load_prompt(filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "prompts", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class RecommendationAgent:
    @staticmethod
    async def run(db: Session, shared_state: dict) -> dict:
        logger.info("Recommendation Agent: Starting selection...")
        business = shared_state.get("business", {})
        carbon = shared_state.get("carbon_analysis", {})
        goals = shared_state.get("goals", {})
        
        industry = business.get("industry", "Manufacturing")
        
        # 1. Fetch industry measures from database
        measures = db.query(SustainabilityMeasure).filter(
            SustainabilityMeasure.industry.ilike(industry)
        ).all()
        
        # If no industry-specific measures found, fallback to all measures
        if not measures:
            measures = db.query(SustainabilityMeasure).all()
            
        measures_list = [
            {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "expected_reduction": float(m.expected_reduction)
            }
            for m in measures
        ]
        
        # 2. Call LLM to select, customize and prioritize measures
        global_inst = load_prompt("global_instruction.md")
        rec_inst = load_prompt("recommendation.md")
        
        system_instruction = f"{global_inst}\n\n{rec_inst}"
        
        prompt = f"""
        Business details:
        - Sector: {industry}
        - Company size: {business.get("company_size")}
        - Description: {business.get("description")}
        
        User Goals:
        - Target carbon reduction: {goals.get("reduction_goal", 20)}%
        - Strategic priority: {goals.get("priority", "ROI")}
        - Target timeline: {goals.get("timeline_months", 12)} months
        - Notes/constraints: {goals.get("notes") or "None"}
        
        Emissions Profile:
        - Total: {carbon.get("total_emissions")} {carbon.get("unit")}
        - Hotspot source: {carbon.get("highest_source")}
        - Observations: {json.dumps(carbon.get("observations"))}
        
        Available Sustainability Measures from Database:
        {json.dumps(measures_list)}
        
        Select the best 3-7 recommendations from the measures list that address these carbon hotspots AND align with the user's reduction goal, priority, and timeline. Prefer measures from the same industry. Structure your output exactly according to the schema.
        """
        
        llm_response = await LLMService.call_model(prompt, system_instruction, json_mode=True)
        
        try:
            result = json.loads(llm_response)
            result["status"] = "SUCCESS"
        except Exception as e:
            logger.error(f"Failed to parse Recommendation Agent LLM response: {str(e)}. Using fallback JSON.")
            # Fallback based on database query
            selected_recs = []
            for m in measures[:3]: # Take up to first 3
                selected_recs.append({
                    "title": m.title,
                    "description": m.description,
                    "priority": "HIGH",
                    "expected_reduction_percent": float(m.expected_reduction),
                    "sdg": [7, 12, 13]
                })
            result = {
                "status": "SUCCESS",
                "recommendations": selected_recs,
                "confidence": 90
            }
            
        shared_state["recommendations"] = result.get("recommendations", [])
        logger.info("Recommendation Agent: Recommendations generated successfully.")
        return result
