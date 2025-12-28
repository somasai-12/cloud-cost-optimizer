from src.validation import validate_report
from src.logger import get_logger

logger = get_logger("report_builder")

def build_cost_optimization_report(profile, analysis, recommendations):

    summary = calculate_summary(recommendations, analysis)

    report = {
        "project_name": profile.get("name", "Unknown"),
        "analysis": analysis,
        "recommendations": recommendations,
        "summary": summary
    }

    is_valid, message = validate_report(report)
    if not is_valid:
        logger.error(f"Report_validation failed: {message}")
        return None
    
    logger.info("✓ Report built and validated")
    return report

def calculate_summary(recommendations, analysis):
    total_savings = sum([rec.get("potential_savings", 0) for rec in recommendations])
    total_cost = analysis.get("total_monthly_cost", 1)

    max_savings_possible = total_cost*0.70

    if total_savings >  max_savings_possible:
        logger.info(f"changed global savings from {total_savings} to {max_savings_possible} (70% limit)")
        total_savings = max_savings_possible

    savings_percentage = (total_savings / total_cost * 100) if total_cost > 0 else 0

    summary = {
        "total_potential_savings": int(total_savings),
        "savings_percentage": round(savings_percentage, 2),
        "recommendations_count": len(recommendations)
    }
    
    return summary