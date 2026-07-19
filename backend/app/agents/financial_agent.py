from sqlalchemy.orm import Session
from app.models.models import SustainabilityMeasure, TechnologyCost
from app.services.llm_service import LLMService
import os
import json
from app.config import logger

def load_prompt(filename: str) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "prompts", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

class FinancialAgent:
    @staticmethod
    async def run(db: Session, shared_state: dict) -> dict:
        logger.info("Financial Agent: Starting valuation...")
        recommendations = shared_state.get("recommendations", [])
        metrics = shared_state.get("metrics", {})
        goals = shared_state.get("goals", {})
        currency_symbol = shared_state.get("currency_symbol", "Rs.")
        
        budget = float(metrics.get("sustainability_budget", 0.0))
        revenue = float(metrics.get("annual_revenue", 0.0))
        
        # 1. Resolve costs for each recommendation
        recommendation_costs = []
        total_cost = 0.0
        total_savings = 0.0
        roi_sums = 0.0
        matched_count = 0
        
        for rec in recommendations:
            title = rec.get("title", "")
            # Find matching measure
            measure = db.query(SustainabilityMeasure).filter(
                SustainabilityMeasure.title.ilike(title)
            ).first()
            
            cost = 250000.0 # INR fallback
            roi = 20.0
            savings = 50000.0
            payback = 5.0
            
            if measure:
                cost_rec = db.query(TechnologyCost).filter(
                    TechnologyCost.measure_id == measure.id
                ).first()
                if cost_rec:
                    cost = float(cost_rec.implementation_cost)
                    savings = float(cost_rec.annual_savings)
                    payback = float(cost_rec.roi_years) # payback in years
                    roi = (savings / cost * 100) if cost > 0 else 20.0
                    
            budget_fit = cost <= budget if budget > 0 else True
            
            recommendation_costs.append({
                "title": title,
                "cost": round(cost, 2),
                "roi": round(roi, 2),
                "budget_fit": budget_fit
            })
            
            total_cost += cost
            total_savings += savings
            roi_sums += roi
            matched_count += 1
            
        avg_roi = (roi_sums / matched_count) if matched_count > 0 else 20.0
        payback_years = (total_cost / total_savings) if total_savings > 0 else 4.0
        
        # 2. Call LLM to evaluate financial budget fit and Observations
        global_inst = load_prompt("global_instruction.md")
        fin_inst = load_prompt("financial.md")
        
        system_instruction = f"{global_inst}\n\n{fin_inst}"
        
        prompt = f"""
        Business Metrics (all amounts in Indian Rupees / INR):
        - Annual Revenue: {currency_symbol}{revenue:,.2f}
        - Sustainability Budget: {currency_symbol}{budget:,.2f}
        
        User Goals:
        - Target reduction: {goals.get("reduction_goal", 20)}%
        - Priority: {goals.get("priority", "ROI")}
        - Timeline: {goals.get("timeline_months", 12)} months
        
        Calculated Financials (INR):
        - Total Estimated Cost: {currency_symbol}{total_cost:,.2f}
        - Total Annual Savings: {currency_symbol}{total_savings:,.2f}
        - Average ROI: {avg_roi:.2f}%
        - Payback Period: {payback_years:.2f} years
        - Recommendation Costs: {json.dumps(recommendation_costs)}
        
        Analyze these figures against the available budget and user priority. Express every money amount in INR using "Rs." (never the ₹ symbol). Return the structured JSON matching the output schema.
        """
        
        llm_response = await LLMService.call_model(prompt, system_instruction, json_mode=True)
        
        try:
            result = json.loads(llm_response)
            # Enforce deterministic calculations
            result["financial_summary"] = {
                "total_cost": round(total_cost, 2),
                "annual_savings": round(total_savings, 2),
                "average_roi": round(avg_roi, 2),
                "payback_years": round(payback_years, 2),
                "currency": "INR"
            }
            result["recommendation_costs"] = recommendation_costs
            result["status"] = "SUCCESS"
        except Exception as e:
            logger.error(f"Failed to parse Financial Agent LLM response: {str(e)}. Using fallback JSON.")
            result = {
                "status": "SUCCESS",
                "financial_summary": {
                    "total_cost": round(total_cost, 2),
                    "annual_savings": round(total_savings, 2),
                    "average_roi": round(avg_roi, 2),
                    "payback_years": round(payback_years, 2),
                    "currency": "INR"
                },
                "recommendation_costs": recommendation_costs,
                "confidence": 90
            }
            
        shared_state["financial_analysis"] = result
        logger.info("Financial Agent: Valuation completed successfully.")
        return result
