# Cloud Cost Optimizer (LLM-Driven)

## Project Overview

This project is a menu-driven CLI tool that uses Large Language Models (LLMs) to optimize cloud costs. It takes a plain-English project description, generates a realistic structured profile and synthetic billing data, and produces multi-cloud cost optimization recommendations.

## Features Implemented

### Mandatory Features

1. **Project Profile Extraction**
   - LLM-driven extraction from free-form text
   - Automatic budget parsing
   - Schema validation for data integrity
   - Output: `project_profile.json`

2. **Synthetic Billing Generation**
   - LLM-generated realistic cloud usage records
   - 12-20 records per project
   - Budget-aware billing
   - Output: `mock_billing.json`

3. **Cost Analysis & Optimization**
   - High-cost service identification
   - Budget variance calculation
   - Over-budget detection
   - 6-10 actionable recommendations

4. **Multi-Cloud Recommendations**
   - 7-10 cost optimization suggestions
   - Multi-cloud alternatives
   - Implementation effort levels 
   - Risk assessment
   - Output: `cost_optimization_report.json`

5. **CLI Orchestrator**
   - Menu-driven interface (5 options)
   - Retry mechanisms on failure
   - User-friendly error messages
   - Comprehensive logging

### Bonus Features Implemented

- **Prompt Retry Logic:** Automatically retries LLM calls with stricter instructions if JSON parsing fails.
- **JSON Schema Validation:** Ensures all LLM outputs (Profile, Billing, Reports) strictly adhere to defined schemas.
- **Multi-Cloud Support:** Recommendations explicitly list alternatives for AWS, Azure, and GCP.
- **HTML Report Export:** Generates a professional HTML report alongside the JSON output.
- **Interactive Budget Validation:** Warns the user via CLI if the extracted budget seems infeasible or incorrect.

## Tech Stack

### Core Technologies
- **Language:** Python 3.10+
- **LLM API:** Hugging Face Inference API
- **Model:** meta-llama/Meta-Llama-3-8B-Instruct
- **Configuration:** python-dotenv
- **Validation:** jsonschema

## Installation & Setup

### Step 1: Clone Repository

```
git clone "https://github.com/somasai-12/cloud-cost-optimizer.git"
cd Cloud Cost Optimizer
```

### Step 2: Create Virtual Environment

### On Windows
```
python -m venv venv
venv\Scripts\activate
```

### On macOS/Linux
```
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```
pip install -r requirements.txt
```

### Step 4: Configure Environment

### Copy example configuration
```
cp .env.example .env
```

### Edit .env with your API key
### Open .env and replace:
### HUGGINGFACE_API_KEY=hf_your_actual_key_here

### Run the application
```
python main.py
```


## complete work flow & CLI Menu Options

```
$ python main.py

1. Enter a new project description
   ↓
   [Enter your project details]
   ↓
   ✓ Project profile extracted
   ✓ File: outputs/project_profile.json

2. Run Complete Cost Analysis
   ↓
   ✓ Billing records generated (15 records)
   ✓ Cost analysis complete
   ✓ Recommendations generated (8 recommendations)
   ✓ Report saved
   ↓
   Outputs:
   - outputs/mock_billing.json
   - outputs/cost_optimization_report.json

3. View Recommendations
   ↓
   [Display all 8 recommendations with details]

4. Export Report
   ↓
   ✓ JSON Report: outputs/cost_optimization_report.json
   ✓ HTML Report: outputs/cost_optimization_report.html

5. Exit
   ↓
   ✓ Cloud Cost Optimizer closed!
  ```

## Tools Used

- Hugging Face Inference API
- Meta LLaMA 3 (8B Instruct)
- Gemini AI (Only for design assistance and validation)

## Example Descriptions Used: 
- I need a website for my college project. MERN stack. Hosted on AWS. Budget is strictly 15,000 INR. Do not exceed.

- We are building a food delivery app for 10,000 users per month. Budget: ₹50,000 per month. Tech stack: Node.js backend, PostgreSQL database,object storage for images, monitoring, and basic analytics. Non-functional requirements: scalability, cost efficiency, uptime monitoring.

## Sample Artifacts (Included in Repository) for first example

- sample_artifacts/project_description.txt
- sample_artifacts/project_profile.json
- sample_artifacts/mock_billing.json
- sample_artifacts/cost_optimization_report.json

## Pre-Submission Checklist

- Code pushed to public GitHub repository - ✅
- All mandatory features implemented - ✅
- CLI workflow tested end-to-end - ✅
- Sample input and output artifacts included - ✅
- README includes setup and usage instructions ✅