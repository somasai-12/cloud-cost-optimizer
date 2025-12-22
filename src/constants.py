#These are used for validation of suggested cloud services by LLM because LLM oftern creates new services which in reality doesnot exists.
#This is just for validation purpose -> taking only generic services but in reality tonnes of services exists which needs to be validated 
#through their api's for real existence

VALID_AWS_SERVICES = {
    "EC2", "RDS", "S3", "Lambda", "CloudWatch", "DynamoDB", "CloudFront", 
    "Route 53", "ELB", "Elastic Load Balancing", "VPC", "SNS", "SQS", 
    "ElastiCache", "EKS", "ECS", "Fargate", "SageMaker", "Glue", "Kinesis",
    "API Gateway", "Cognito", "IAM", "KMS", "Secrets Manager"
}

VALID_AZURE_SERVICES = {
    "Virtual Machines", "Azure SQL Database", "Blob Storage", "App Service", 
    "Azure Functions", "Cosmos DB", "Azure Kubernetes Service (AKS)", 
    "Azure Monitor", "Cost Management", "Azure Active Directory", "VNet"
}

VALID_GCP_SERVICES = {
    "Compute Engine", "Cloud SQL", "Cloud Storage", "App Engine", 
    "Cloud Functions", "Firestore", "BigQuery", "Kubernetes Engine (GKE)", 
    "Cloud Run", "Cloud Logging", "Cloud Monitoring", "VPC"
}

SERVICE_MAPPING = {
    "compute": {"aws": "EC2", "azure": "Virtual Machines", "gcp": "Compute Engine"},
    "database": {"aws": "RDS", "azure": "Azure SQL Database", "gcp": "Cloud SQL"},
    "storage": {"aws": "S3", "azure": "Blob Storage", "gcp": "Cloud Storage"},
    "serverless": {"aws": "Lambda", "azure": "Azure Functions", "gcp": "Cloud Functions"},
    "networking": {"aws": "VPC", "azure": "VNet", "gcp": "VPC"},
    "monitoring": {"aws": "CloudWatch", "azure": "Azure Monitor", "gcp": "Cloud Monitoring"},
    "cache": {"aws": "ElastiCache", "azure": "Azure Cache for Redis", "gcp": "Memorystore"},
    "cdn": {"aws": "CloudFront", "azure": "Azure CDN", "gcp": "Cloud CDN"}
}