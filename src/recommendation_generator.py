from src.llm_utils import call_llm_with_auto_retry, robust_json_parse
from src.validation import validate_recommendation
from src.logger import get_logger

logger = get_logger("recommendation_generator")

def generate_recommendations(profile, billing, analysis):

    billed_services = {
        record.get("service").lower()
        for record in billing
        if record.get("service")
    }

    high_cost_services = analysis.get("high_cost_services", {})
    service_costs = analysis.get("service_costs",{})
    total_cost = analysis.get("total_monthly_cost", 0)
    budget = analysis.get("budget", 0)

    services_str = ", ".join([f"{s}: ₹{c}" for s, c in service_costs.items()])
    high_cost_services_str = ", ".join([f"{s}: ₹{c}" for s, c in high_cost_services.items()])

    prompt = f"""Analyze this project's cloud costs and generate optimization recommendations.

Project: {profile.get('name')}
Total Monthly Cost: ₹{total_cost}
Budget: ₹{budget}
All services and montly cost: {services_str}
High-Cost Services (PRIORITY): {high_cost_services_str}
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
- cloud_providers: array of strings listing cloud providers AND valid alternate cloud providers with OPEN SOURCE if applicable.

IMPORTANT REQUIREMENTS:
1. Generate 7-10 recommendations
2. Prioritize high-cost services, but DO NOT skip remaining services.
3. Include multi-cloud and **prioritize open-source recommendations** wherever if both applicable. Donot Restrict cloud providers to AWS only.
4. Potential savings should be realistic (10-50% of current cost)
5. All steps should be actionable
6. Do NOT invent abstract services (e.g., images, logs, files) **service should be from input services only donot invent new names**.
7. Do NOT restrict recommendations only to high-cost services; Include remaining services where meaningful optimizations exist.
8. The "service" MUST be one of the services listed under "All Services and Monthly Costs".
9. For the "cloud_providers" field, ALWAYS list the current provider plus at least one or two competitor or "Open Source" if applicable.
10. **NO TAUTOLOGIES**: Do NOT recommend migrating *to* the service already being used. (e.g., If service is "AWS RDS", do NOT recommend "Migrate to AWS RDS").

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
        if service and str(service).lower() not in billed_services:
            logger.warning(f"Skipping hallucinated service '{service}'")
            continue

        current_cost = rec.get("current_cost", 0)
        if current_cost <= 0:
            logger.warning(f"Skipping recommendation '{rec.get('title')}' due to zero or invalid current_cost")
            continue
        potential_savings = rec.get("potential_savings", 0)

        max_savings = current_cost * 0.60
        if potential_savings > max_savings:
            rec["potential_savings"] = int(max_savings)
            logger.info(f"changed savings for '{rec.get('title')}' to {rec['potential_savings']} (Max 60%)")
        
        clouds = rec.get("cloud_providers")
        if not isinstance(clouds, list) or not clouds:
            logger.warning("Recommendation missing cloud_providers")
            continue
        
        is_valid, message = validate_recommendation(rec)
        if not is_valid:
            logger.warning(f"Skipping invalid recommendation {i}: {message}")
            continue

        valid_recommendations.append(rec)

    
    logger.info(f"✓ Generated {len(valid_recommendations)} valid recommendations")
    return valid_recommendations