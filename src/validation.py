from jsonschema import validate, ValidationError
from src.logger import get_logger

logger = get_logger("validation")

PROJECT_PROFILE_SCHEMA = {
    "type": "object",
    "required": ["name", "budget_inr_per_month", "description", "tech_stack", "non_functional_requirements"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "budget_inr_per_month": {"type": "number", "minimum": 100},
        "description": {"type": "string", "minLength": 10},
        "tech_stack": {
            "type": "object",
            "additionalProperties": {"type": "string"}
        },
        "non_functional_requirements": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        }
    }
}

BILLING_RECORD_SCHEMA = {
    "type": "object",
    "required": ["month", "service", "resource_id", "region", "usage_type", "usage_quantity", "unit", "cost_inr", "desc"],
    "properties": {
        "month": {"type": "string", "pattern": "^\\d{4}-\\d{2}$"},
        "service": {"type": "string"},
        "resource_id": {"type": "string"},
        "region": {"type": "string"},
        "usage_type": {"type": "string"},
        "usage_quantity": {"type": "number", "minimum": 0},
        "unit": {"type": "string"},
        "cost_inr": {"type": "number", "minimum": 0},
        "desc": {"type": "string"}
    }
}

RECOMMENDATION_SCHEMA = {
    "type": "object",
    "required": ["title", "service", "current_cost", "potential_savings", "recommendation_type", 
                 "description", "implementation_effort", "risk_level", "steps", "cloud_providers"],
    "properties": {
        "title": {"type": "string"},
        "service": {"type": "string"},
        "current_cost": {"type": "number"},
        "potential_savings": {"type": "number"},
        "recommendation_type": {
            "type": "string",
            "enum": ["opensource", "free_tier", "alternative_provider", "right_sizing", "optimization", "cost-effective_storage"]
        },
        "description": {"type": "string"},
        "implementation_effort": {"type": "string", "enum": ["low", "medium", "high"]},
        "risk_level": {"type": "string", "enum": ["low", "medium", "high"]},
        "steps": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 3,
            "maxItems": 5
        },
        "cloud_providers": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        }
    }
}

REPORT_SCHEMA = {
    "type": "object",
    "required": ["project_name", "analysis", "recommendations", "summary"],
    "properties": {
        "project_name": {"type": "string"},
        "analysis": {
            "type": "object",
            "required": ["total_monthly_cost", "budget", "budget_variance", "service_costs", "high_cost_services", "is_over_budget"],
            "properties": {
                "total_monthly_cost": {"type": "number"},
                "budget": {"type": "number"},
                "budget_variance": {"type": "number"},
                "service_costs": {"type": "object"},
                "high_cost_services": {"type": "object"},
                "is_over_budget": {"type": "boolean"}
            }
        },
        "recommendations": {
            "type": "array",
            "items": RECOMMENDATION_SCHEMA,
            "minItems": 6,
            "maxItems": 10
        },
        "summary": {
            "type": "object",
            "required": ["total_potential_savings", "savings_percentage", "recommendations_count"],
            "properties": {
                "total_potential_savings": {"type": "number"},
                "savings_percentage": {"type": "number"},
                "recommendations_count": {"type": "integer"}
            }
        }
    }
}

def validate_profile(profile):
    try:
        validate(instance=profile, schema=PROJECT_PROFILE_SCHEMA)
        return True, "profile is valid"
    except ValidationError as e:
        return False, f"Profile validation failed: {e.message}"

def validate_billing(billing):
    try:
        if not isinstance(billing, list):
            return False, "Billing must be an array"
        if len(billing) < 12 or len(billing)>20:
            return False, f"Billing must have 12-20 records, got {len(billing)}"
        for i, record in enumerate(billing):
            validate(instance=record, schema=BILLING_RECORD_SCHEMA)

        return True, "Billing is Valid"
    except ValidationError as e:
        return False, f"Billing validation failed at record {i}: {e.message}"
    

def validate_recommendation(recommendation):
    try:
        validate(instance=recommendation, schema=RECOMMENDATION_SCHEMA)
        return True, "Recommendation is Valid"
    except ValidationError as e:
        return False, f"Recommendation Valid Failed: {e.message}"
    

def validate_report(report):
    try:
        validate(instance=report, schema=REPORT_SCHEMA)
        return True, "Report is Valid"
    except ValidationError as e:
        return False, f"Report Validation Failed: {e.message}"
    
