import json
import re
import time
import requests
from src.config import HUGGINGFACE_API_KEY, LLM_MODEL, API_TIMEOUT, MAX_RETRIES, RETRY_DELAY_SECONDS
from src.logger import get_logger

logger = get_logger("llm_utils")

def call_huggingface_api(prompt, model=None):
    if model is None:
        model = LLM_MODEL
    
    api_url = "https://router.huggingface.co/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    } 
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=API_TIMEOUT
        )

        if response.status_code == 429:
            logger.warning("Rate limited (429). Waiting before retry...")
            return None
        
        if response.status_code == 404:
            logger.error("API endpoint not found (404).")
            return None
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
            logger.error(f"Unexpected response: {result}")
            return None        

        logger.error(f"API Error {response.status_code}: {response.text}")
        return None

    except requests.exceptions.Timeout:
        logger.error("API request timeout")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Connection error")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"API call error: {e}")
        return None    

def clean_json_string(json_str):

    if not json_str:
        return ""
    
    json_str = re.sub(r'```(?:json)?', '', json_str)
    json_str = re.sub(r'```', '', json_str)
    json_str = json_str.strip()
    start_idx = -1
    end_idx = -1
    
    for i, char in enumerate(json_str):
        if char in ['{', '[']:
            start_idx = i
            break
            
    for i in range(len(json_str) - 1, -1, -1):
        if json_str[i] in ['}', ']']:
            end_idx = i
            break
            
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = json_str[start_idx:end_idx+1]
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    return json_str

def robust_json_parse(response_text):
    if not response_text:
        return None
    try:
        return json.loads(response_text, strict=False)
    except json.JSONDecodeError:
        pass

    cleaned_text = clean_json_string(response_text)
    try:
        return json.loads(cleaned_text, strict=False)
    except json.JSONDecodeError:
        pass
        
    try:
        match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if match:
            obj_str = clean_json_string(match.group(1))
            return json.loads(obj_str, strict=False)
        match = re.search(r'(\[.*\])', response_text, re.DOTALL)
        if match:
            arr_str = clean_json_string(match.group(1))
            return json.loads(arr_str, strict=False)
    except Exception:
        pass
        
    logger.warning("Could not extract valid JSON from response")
    return None

def call_llm_with_auto_retry(prompt, max_retries=MAX_RETRIES):
    retry_count = 0
    current_prompt = prompt
    
    while retry_count < max_retries:
        response = call_huggingface_api(current_prompt)
        
        if response is None:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = RETRY_DELAY_SECONDS * (2 ** retry_count)
                logger.info(f"Retry {retry_count}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)
            continue
        
        data = robust_json_parse(response)
        if data:
            #return response 
            return json.dumps(data) #ensuring that next files can safely get only json
        
        retry_count += 1
        if retry_count < max_retries:
            current_prompt = f"{prompt}\n\nCRITICAL ERROR: Your previous response was not valid JSON. \n\nRETURN ONLY RAW JSON. NO MARKDOWN. NO COMMENTS.\nEnsure no trailing commas."
            wait_time = RETRY_DELAY_SECONDS * (2 ** retry_count)
            logger.info(f"JSON parsing failed. Retrying with stricter prompt in {wait_time}s...")
            time.sleep(wait_time)
    
    logger.error(f"Failed after {max_retries} retries")
    return None