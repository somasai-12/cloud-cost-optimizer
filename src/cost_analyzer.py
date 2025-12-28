from src.logger import get_logger

logger = get_logger("cost_analyzer")

def analyze_costs(profile, billing):

    budget = profile.get("budget_inr_per_month")

    if not isinstance(budget, (int, float)):
        logger.error("Budget missing or invalid in project profile")
        return None

    service_costs = calculate_service_costs(billing)

    total_cost = sum(service_costs.values())

    variance = total_cost - budget

    high_cost_services = {}

    if total_cost > 0:
        for service, cost in service_costs.items():
            percentage = (cost/total_cost)*100
            if percentage>15:
                high_cost_services[service] = int(cost)

    is_over_budget = total_cost > budget

    analysis = {
        "total_monthly_cost": int(total_cost),
        "budget": budget,
        "budget_variance": int(variance),
        "service_costs": {k: int(v) for k, v in service_costs.items()},
        "high_cost_services": high_cost_services,
        "is_over_budget": is_over_budget
    }

    logger.info(f"✓ Cost analysis complete - Total: ₹{analysis['total_monthly_cost']}")
    return analysis

def calculate_service_costs (billing):
    service_costs = {}

    for record in billing:
        service = record.get("service", "Unknown")
        cost = record.get("cost_inr", 0)

        if service not in service_costs:
            service_costs[service] = 0
            
        service_costs[service] += cost
    
    return service_costs