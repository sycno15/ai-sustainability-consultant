from sqlalchemy.orm import Session
from app.models.models import EmissionFactor
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
        if filename == "carbon.md":
            return "Carbon Assessment Agent: Calculate GHG footprint and emissions breakdown."
        return "Sustainability System Directives: Provide output formatted strictly as JSON."

class CarbonAgent:
    @staticmethod
    async def run(db: Session, shared_state: dict) -> dict:
        logger.info("Carbon Agent: Starting analysis...")
        metrics = shared_state.get("metrics", {})
        business = shared_state.get("business", {})
        
        # 1. Fetch emission factors from database with fallbacks
        try:
            factors = db.query(EmissionFactor).all()
            factor_map = {
                f.activity.lower(): float(f.emission_factor) 
                for f in factors if f and getattr(f, "activity", None) and getattr(f, "emission_factor", None) is not None
            }
        except Exception as e:
            logger.warning(f"Carbon Agent: DB query for emission factors failed ({e}). Using standard fallbacks.")
            factor_map = {}
        
        # Enforce ponytail philosophy: standard fallbacks if db factors are empty
        electricity_factor = factor_map.get("electricity", 0.42)
        diesel_factor = factor_map.get("diesel", 2.68)
        petrol_factor = factor_map.get("petrol", 2.31)
        water_factor = factor_map.get("water", 0.34)
        waste_factor = factor_map.get("waste", 0.52)
        
        # Helper safely parsing numeric metric values
        def safe_float(val) -> float:
            try:
                return float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                return 0.0

        # 2. Calculate emissions deterministically
        electricity_emissions = safe_float(metrics.get("electricity_usage")) * electricity_factor
        diesel_emissions = safe_float(metrics.get("diesel_usage")) * diesel_factor
        petrol_emissions = safe_float(metrics.get("petrol_usage")) * petrol_factor
        water_emissions = safe_float(metrics.get("water_usage")) * water_factor
        waste_emissions = safe_float(metrics.get("waste_generated")) * waste_factor
        
        total_emissions = electricity_emissions + diesel_emissions + petrol_emissions + water_emissions + waste_emissions
        
        breakdown = [
            {"activity": "Electricity", "emissions": electricity_emissions},
            {"activity": "Diesel", "emissions": diesel_emissions},
            {"activity": "Petrol", "emissions": petrol_emissions},
            {"activity": "Water", "emissions": water_emissions},
            {"activity": "Waste", "emissions": waste_emissions}
        ]
        
        # Identify highest emitting source
        highest_source = max(breakdown, key=lambda x: x["emissions"])["activity"]
        
        # 3. Call LLM to write observations and format return JSON
        global_inst = load_prompt("global_instruction.md")
        carbon_inst = load_prompt("carbon.md")
        
        system_instruction = f"{global_inst}\n\n{carbon_inst}"
        
        prompt = f"""
        Business Context:
        - Industry: {business.get("industry")}
        - Size: {business.get("company_size")}
        
        Calculated Carbon Data:
        - Total Emissions: {total_emissions:.2f} kgCO2e/year
        - Highest Contributing Source: {highest_source}
        - Emission Breakdown: {json.dumps(breakdown)}
        
        Write observations explaining these emissions relative to the business size and sector, and output the result.
        """
        
        llm_response = await LLMService.call_model(prompt, system_instruction, json_mode=True)
        
        try:
            result = LLMService.clean_and_parse_json(llm_response)
            # Ensure calculations in final JSON are the deterministic ones we computed
            result["total_emissions"] = round(total_emissions, 2)
            result["breakdown"] = [
                {"activity": b["activity"], "emissions": round(b["emissions"], 2)}
                for b in breakdown
            ]
            result["highest_source"] = highest_source
            result["status"] = "SUCCESS"
        except Exception as e:
            logger.error(f"Failed to parse Carbon Agent LLM response: {str(e)}. Using fallback JSON.")
            result = {
                "status": "SUCCESS",
                "total_emissions": round(total_emissions, 2),
                "unit": "kgCO2e/year",
                "breakdown": [{"activity": b["activity"], "emissions": round(b["emissions"], 2)} for b in breakdown],
                "highest_source": highest_source,
                "observations": [f"Emissions are highest for {highest_source}."],
                "confidence": 90
            }
            
        shared_state["carbon_analysis"] = result
        logger.info("Carbon Agent: Analysis completed successfully.")
        return result
