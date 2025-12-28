from src.llm_utils import call_llm_with_auto_retry
from src.validation import validate_profile
from src.logger import get_logger
import json
import re

logger = get_logger("profile_extractor")

def extract_project_profile(description):

    prompt = f"""You are a cloud Architect. Extract the project details from this description and return ONLY a Valid JSON object. Follow important points mentioned as IMPORTANT.

Description: {description}

### You MUST return a valid JSON object with these exact fields:
- **name**: (string) Project name extracted from description which is a Short, professional project name.
- **budget_inr_per_month**:Extract the numeric monthly budget in INR (e.g., "50k", "50,000", "5 lakhs")which is integer. 
                           Monthly budget in INR. **Important** Value mentioned should be from description only. 
                           Handle Indian numbering (e.g. "6,00,000" -> 600000). Remove ALL commas and symbols.
                           (Important) If not mentioned donot return this field.
- **description**: (string) Brief description of the project which is concise 1-sentence summary of given project purpose, Do NOT copy the input text verbatim.
- **tech_stack**: (dictionary) Key-Value pairs of technology. Capture ALL languages, frameworks, and tools mentioned (e.g., "language": "C++, Python", "cloud": "AWS ParallelCluster etc..") by Categorizing the technologies into specific roles and choose appropriate keys for technologies.
                  **CRITICAL**: Expand acronyms! (e.g., "MERN" -> MongoDB, Express.js, React, Node.js).
- **non_functional_requirements**: (array of strings) List of NFRs (e.g., ["Scalability", "Tolerant", "Security"]) if not explicitly stated

Return ONLY the JSON object, nothing else. No markdown, no explanations, no extra other than required valid JSON object.

Example format(For format only):
{{
  "name": "Food Delivery App",
  "budget_inr_per_month": 50000,
  "description": "A scalable mobile application for local food delivery.",
  "tech_stack": {{
      "frontend": "React",
      "backend": "Node.js",
      "database": "PostgreSQL",
      "cloud": "AWS"
  }},
  "non_functional_requirements": ["Scalability", "Cost Efficiency", "High Availability"]
}}

-Important:
1. If no budget(in INR or ₹) is present in description then donot return JSON object only.

Now extract from the description above: and Return ONLY the JSON object. No markdown."""
    
    try:
        logger.info("Extracting project profile...")

        response = call_llm_with_auto_retry(prompt)

        if response is None:
            logger.error("Failed to get response from LLM")
            return None
        
        try:
            profile = json.loads(response, strict=False)
            budget_match = re.search(r'budget\s*(?:is|of|:)?\s*[\D]*([\d,]+(?:\.\d+)?)', description, re.IGNORECASE)
            if budget_match:
                raw_budget_str = budget_match.group(1)
                clean_budget_str = raw_budget_str.replace(",","")
                try:
                    regex_budget = int(float(clean_budget_str))
                    llm_budget = profile.get("budget_inr_per_month", 0)
                    if llm_budget == 0:
                        return None
                    if llm_budget != regex_budget:
                        logger.error(f"Mismatch! LLM: {llm_budget}, Regex: {regex_budget}")
                        print(f"\n[!] Budget Mismatch: You wrote '{raw_budget_str}' ({regex_budget}), but LLM extracted {llm_budget}.")
                        profile["budget_inr_per_month"] = regex_budget
                
                except ValueError:
                    pass

            raw_budget = profile.get("budget_inr_per_month")
            if not isinstance(raw_budget,(int,float)):
                logger.error(
                    "LLM did not return a valid numeric budget_inr_per_month."
                )
                return None
            if isinstance(raw_budget, str):
                try:
                    clean_budget = raw_budget.replace(",", "").replace("₹", "").replace("INR", "").strip()
                    profile["budget_inr_per_month"] = int(float(clean_budget))
                except ValueError:
                    logger.warning(f"Could not parse budget string: {raw_budget}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from LLM: {e}")
            return None
        
        is_valid, msg = validate_profile(profile)
        if not is_valid:
            logger.error("Profile validation failed: Schema mismatch")
            return None
        
        if not profile.get("non_functional_requirements"):
            logger.error("Missing non-functional requirements")
            return None

        logger.info("✓ Project profile extracted successfully")
        return profile

    except Exception as e:
        logger.error(f"Error extracting profile: {e}")
        return None