import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 60))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 25))
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", 2))

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./outputs")
SAMPLE_DIR = os.getenv("SAMPLE_DIR", "./sample_artifacts")

Path(OUTPUT_DIR).mkdir(exist_ok=True)
Path(SAMPLE_DIR).mkdir(exist_ok=True)

DESCRIPTION_FILE = os.path.join(OUTPUT_DIR, "project_description.txt")
PROFILE_FILE = os.path.join(OUTPUT_DIR, "project_profile.json")
BILLING_FILE = os.path.join(OUTPUT_DIR, "mock_billing.json")
REPORT_FILE = os.path.join(OUTPUT_DIR, "cost_optimization_report.json")

REAL_SERVICES = [
    "EC2", "RDS", "S3", "Lambda", "CloudWatch", "Load Balancer",
    "Networking", "VPC", "Route53", "CloudFront", "DynamoDB",
    "Elasticache", "Kinesis", "SQS", "SNS", "EMR", "Redshift",
    "Glue", "Athena", "QuickSight", "Sage Maker", "AppSync"
]

RECOMMENDATION_TYPES = [
    "opensource",
    "free_tier",
    "alternative_provider",
    "right_sizing",
    "optimization",
    "cost-effective_storage"
]

EFFORT_LEVELS = ["low", "medium", "high"]
RISK_LEVELS = ["low", "medium", "high"]
CLOUD_PROVIDERS = ["AWS", "Azure", "GCP", "Open Source"]

def check_configuration():
    if not HUGGINGFACE_API_KEY:
        raise ValueError(
            "ERROR: HUGGINGFACE_API_KEY not found in .env file!\n"
        )
    if not LLM_MODEL:
        raise ValueError("ERROR: LLM_MODEL not configured")