from src.llm_utils import call_llm_with_auto_retry, robust_json_parse
from src.validation import validate_billing
from src.logger import get_logger
import random
import datetime

logger = get_logger("billing_generator")

def generate_billing(profile):

    budget = profile.get("budget_inr_per_month", 50000)
    logger.info(f"Generating billing records for budget: {budget}")

    tech_stack = profile.get("tech_stack", {})
    if isinstance(tech_stack,list):
        tech_stack_str = ", ".join(tech_stack)
    elif isinstance(tech_stack, dict):
        tech_stack_str = ", ".join([f"{k}: {v}" for k,v in tech_stack.items()])
    else:
        tech_stack_str = str(tech_stack)

    current_month = datetime.datetime.now().strftime("%Y-%m")

    cloud_provider = "AWS" #default value
    if "Azure" in tech_stack_str or "Microsoft" in tech_stack_str:
        cloud_provider = "Azure"
    elif "GCP" in tech_stack_str or "Google" in tech_stack_str:
        cloud_provider = "GCP"
    #logger.info(f"Detected Cloud Provider: {cloud_provider}")

    prompt = f"""Generate realistic cloud usage data for this project.

    Project: {profile.get('name')}
    Tech Stack: {tech_stack_str}
    Description: {profile.get('description')}
    Target Cloud: {cloud_provider}
    Generate a JSON array with 12-15 usage records for the MONTH of {current_month}.
    Each record must have:
    - month: "{current_month}" (All records must be for the same month)
    - service: Valid {cloud_provider} service name (e.g. if Azure: "Virtual Machines", "Blob Storage"; if AWS: "EC2", "S3")
    - resource_id: unique identifier
    - region: "ap-south-1" or related ones accordingly
    - usage_type: description of what is being used
    - usage_quantity: number (e.g. 720, 50, 1000)
    - unit: "hours", "GB", "requests"
    - desc: brief description
    - importance: 1-10 (how critical this service is, used for cost weighting)
    
    Do NOT include cost.
    Return ONLY JSON array."""
    
    logger.info("Generating billing records...")

    response = call_llm_with_auto_retry(prompt)

    if not response:
        logger.error("Failed to get response from LLM")
        return None
    
    billing_data = robust_json_parse(response)

    if not billing_data or not isinstance(billing_data, list):
        logger.error("Failed to parse billing data given by LLM")
        return None
    
    total_importance = sum(item.get('importance', 5) for item in billing_data)
    if total_importance == 0: total_importance = 1

    actual_monthly_cost = budget * random.uniform(0.95, 1.05)

    final_billing = []
    current_total = 0

    for i, item in enumerate(billing_data):
        importance = item.get('importance', 5)

        share = (importance/total_importance) * actual_monthly_cost

        cost = round(share,2)

        if i==len(billing_data) - 1:
            cost = round(actual_monthly_cost - current_total, 2)
            if cost<0: cost = 100 
        
        current_total+=cost

        item['cost_inr'] = cost
        if 'importance' in item:
            del item['importance']
        
        final_billing.append(item)
    
    billing = final_billing

    is_valid, message = validate_billing(billing)
    if not is_valid:
        logger.error(f"Billing validation failed: {message}")
        return None
    
    logger.info(f"✓ Generated {len(billing)} billing records with calculated costs")
    return billing