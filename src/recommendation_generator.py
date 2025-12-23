from src.llm_utils import call_llm_with_auto_retry, robust_json_parse
from src.validation import validate_recommendation
from src.logger import get_logger
from src.constants import VALID_AWS_SERVICES, VALID_AZURE_SERVICES, VALID_GCP_SERVICES

logger = get_logger("recommendation_generator")

def generate_recommendations(profile, billing, analysis):

    high_cost_services = analysis.get("high_cost_services", {})
    service_costs = analysis.get("service_costs",{})
    total_cost = analysis.get("total_monthly_cost", 0)
    budget = analysis.get("budget", 0)

    services_str = ", ".join([f"{s}: ₹{c}" for s, c in high_cost_services.items()])

    prompt = f"""Analyze this project's cloud costs and generate optimization recommendations.

Project: {profile.get('name')}
Total Monthly Cost: ₹{total_cost}
Budget: ₹{budget}
High-Cost Services: {services_str}
Tech Stack: {profile.get('tech_stack', {})}

Generate a JSON array with 7-10 cost optimization recommendations.
Each recommendation must have EXACTLY these fields:
- title: string (recommendation title)
- service: string (which service this affects)
- current_cost: number (current monthly cost)
- potential_savings: number (estimated monthly savings in INR)
- recommendation_type: one of [opensource, free_tier, alternative_provider, right_sizing, optimization, cost-effective_storage]
- description: string (detailed explanation)
- implementation_effort: one of [low, medium, high]
- risk_level: one of [low, medium, high]
- steps: array of 3-5 implementation steps as strings
- cloud_providers: array of cloud providers (AWS, Azure, GCP, Open Source)

REQUIREMENTS:
1. Generate 7-10 recommendations
2. Focus on high-cost services first
3. Include at least 2 recommendations for multi-cloud migration
4. Potential savings should be realistic (10-50% of current cost)
5. All steps should be actionable

Return ONLY the JSON array, no extra text or markdown."""
    
    logger.info("Generating recommendation...")

    response = call_llm_with_auto_retry(prompt)

    if not response:
        logger.error("Failed to get response from LLM")
        return None
    
    recommendations = robust_json_parse(response)

    if not recommendations:
        logger.error("Failed to parse response as JSON")
        return None
    
    if not isinstance(recommendations, list):
        logger.error("Response is not an array")
        return None
    
    valid_recommendations = []

    for i,rec in enumerate(recommendations):
        service = rec.get("service")
        if service:
            is_valid_service = (service in VALID_AWS_SERVICES or 
                                service in VALID_AZURE_SERVICES or 
                                service in VALID_GCP_SERVICES)
            
            if not is_valid_service:
                known_generics = ["AWS", "Azure", "GCP", "Open Source", "DigitalOcean"]
                if service not in known_generics: 
                     logger.warning(f"Potential hallucinated service: {service}. Checking if close match...")
                     pass
                
        rec_type = rec.get("recommendation_type")

        if rec_type== "open_source":
            rec["cloud_providers"] = ["Open Source"]
        elif rec_type== "free_tier":
            rec["cloud_providers"] = ["AWS"]
        elif rec_type == "alternative_provider":
            rec["cloud_providers"] = ["GCP", "Azure", "DigitalOcean"]
            
        elif rec_type == "right_sizing" or rec_type == "optimization":
            if "AWS" not in rec.get("cloud_providers", []):
                rec["cloud_providers"] = ["AWS", "Azure", "GCP"]

        current_cost = rec.get("current_cost", 0)
        potential_savings = rec.get("potential_savings", 0)

        max_savings = current_cost * 0.50
        if potential_savings > max_savings:
            rec["potential_savings"] = round(max_savings, 2)
            logger.info(f"Capped savings for '{rec.get('title')}' to {rec['potential_savings']} (Max 50%)")
        
        is_valid, message = validate_recommendation(rec)
        if not is_valid:
            logger.warning(f"Skipping invalid recommendation {i}: {message}")
            continue

        valid_recommendations.append(rec)

    
    logger.info(f"✓ Generated {len(valid_recommendations)} valid recommendations")
    return valid_recommendations