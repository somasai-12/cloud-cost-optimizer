from src.llm_utils import call_llm_with_auto_retry
from src.validation import validate_profile
from src.logger import get_logger
import json
import re

logger = get_logger("profile_extractor")

def extract_project_profile(description):

    prompt = f"""Extract the project details from this description and return ONLY a Valid JSON object.

Description: {description}

You MUST return a valid JSON object with these exact fields:
- name: (string) Project name extracted from description
- budget_inr_per_month: (integer) Monthly budget in INR. Handle Indian numbering (e.g. "6,00,000" -> 600000). Remove ALL commas and symbols. Estimate if not explicit.
- description: (string) Brief description of the project
- tech_stack: (dictionary) Key-Value pairs of technology. Capture ALL languages, frameworks, and tools mentioned (e.g., "language": "C++, Python etc..", "cloud": "AWS ParallelCluster etc..").
- non_functional_requirements: (array of strings) List of NFRs (e.g., ["Scalability", "Tolerant", etc..])

Return ONLY the JSON object, nothing else. No markdown, no explanations, no extra other than required valid JSON object.

Example format:
{{
  "name": "Food Delivery App",
  "budget_inr_per_month": 50000,
  "description": "Mobile app for food delivery",
  "tech_stack": {{
      "frontend": "React",
      "backend": "Node.js",
      "database": "PostgreSQL",
      "cloud": "AWS"
  }},
  "non_functional_requirements": ["Scalability", "Cost Efficiency", "High Availability"]
}}

Now extract from the description above:"""
    
    try:
        logger.info("Extracting project profile...")

        response = call_llm_with_auto_retry(prompt)

        if response is None:
            logger.error("Failed to get response from LLM")
            return None
        
        try:
            profile = json.loads(response, strict=False)
            import re
            budget_match = re.search(r'budget\s*(?:is|of|:)?\s*[\D]*([\d,]+)', description, re.IGNORECASE)
            if budget_match:
                raw_budget_str = budget_match.group(1)
                clean_budget_str = raw_budget_str.replace(",","").replace(".","") #-> simple interger
                try:
                    regex_budget = int(clean_budget_str)
                    llm_budget = profile.get("budget_inr_per_month", 0)

                    if not isinstance(llm_budget, (int,float)) or llm_budget != regex_budget:
                        logger.info(f"Regex override: LLM said {llm_budget}, Regex found {regex_budget} from '{raw_budget_str}'")
                        profile["budget_inr_per_month"] = regex_budget
                
                except ValueError:
                    pass

            raw_budget = profile.get("budget_inr_per_month")
            if isinstance(raw_budget, str):
                try:
                    clean_budget = raw_budget.replace(",", "").replace("₹", "").replace("INR", "").strip()
                    profile["budget_inr_per_month"] = int(float(clean_budget))
                    logger.info(f"Fixed budget format: '{raw_budget}' -> {profile['budget_inr_per_month']}")
                except ValueError:
                    logger.warning(f"Could not parse budget string: {raw_budget}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from LLM: {e}")
            #logger.error(f"Response was: {response[:200]}") -> debugging responses received
            return None
        

        if not validate_profile(profile):
            logger.error("Profile validation failed: Schema mismatch")
            return None

        logger.info("✓ Project profile extracted successfully")
        return profile

    except Exception as e:
        logger.error(f"Error extracting profile: {e}")
        return None