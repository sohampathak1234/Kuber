import os
import re
from typing import Dict, Any
from dotenv import load_dotenv
from groq import Groq

# ========== Load Environment ==========
load_dotenv("own_agents/creds.env")

API_KEY = os.getenv("categorizing_agent_groq_api")
MODEL_NAME = os.getenv("model_name")

if not API_KEY:
    raise EnvironmentError("❌ 'categorizing_agent_groq_api' not found in .env.")
if not MODEL_NAME:
    raise EnvironmentError("❌ 'model_name' not found in .env.")

client = Groq(api_key=API_KEY)


# ========== Prompt Builder ==========
def build_prompt(subject: str, body: str) -> str:
    return f"""
You are a strict email categorizer and personal info extractor.

Your task is:
1. Understand the **context** of the email (from subject and body).
2. Categorize it into ONE of these:
   - FI Money app enquiry
   - Financial Advice
   - Goal planning
   - SIP Advice
   - Stock trading advice
   - Non-standard (phish email)
3. Extract:
   - Name (if any)
   - Phone number (if any)
4. Return response as JSON in this format:
   {{
     "category": "...",
     "name": "...",
     "phone": "..."
   }}

Only respond with JSON. Do not explain.

Email Subject: {subject}

Email Body:
{body}
""".strip()


# ========== Core Categorization Function ==========
def categorize_email(subject: str, body: str) -> Dict[str, Any]:
    prompt = build_prompt(subject, body)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an accurate email categorizer."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        # Optional: validate JSON pattern using regex
        json_pattern = r'^\{[\s\S]*\}$'
        if not re.match(json_pattern, content):
            raise ValueError("Invalid JSON returned by model.")

        # Use eval safely since format is strict JSON-like
        result = eval(content, {"__builtins__": {}})
        if not isinstance(result, dict):
            raise ValueError("Response is not a valid dictionary.")

        return {
            "category": result.get("category", "").strip(),
            "name": result.get("name", "").strip(),
            "phone": result.get("phone", "").strip()
        }

    except Exception as e:
        return {
            "category": "Non-standard (phish email)",
            "name": "",
            "phone": ""
        }


# ========== Example Test ==========
# if __name__ == "__main__":
#     subject = "Looking for investment options for my child's future"
#     body = """
# Hi Team,

# I'm exploring investment avenues to save for my child's higher education. I heard about SIPs but I need expert advice on how to proceed and what funds would be best suited.

# Regards,
# Nikhil Sharma
# Phone: 9876543210
# """

#     result = categorize_email(subject, body)
#     print(result)
