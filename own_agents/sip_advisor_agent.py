import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from groq import Groq


# ========== Load Environment Variables ==========
load_dotenv("own_agents/creds.env")

API_KEY = os.getenv("sip_advisor_api")
MODEL_NAME = os.getenv("model_name")

if not API_KEY:
    raise EnvironmentError("❌ 'sip_advisor_api' not found in .env file.")
if not MODEL_NAME:
    raise EnvironmentError("❌ 'model_name' not found in .env file.")


# ========== Initialize Groq Client ==========
client = Groq(api_key=API_KEY)


# ========== Fetch Mutual Fund List ==========
def fetch_top_mutual_funds(count: int = 15) -> List[Dict[str, Any]]:
    """
    Fetch top mutual fund schemes using MFAPI.
    Filters for equity-related schemes for SIP suitability.
    """
    try:
        response = requests.get("https://api.mfapi.in/mf", timeout=10)
        response.raise_for_status()
        all_funds = response.json()

        if not isinstance(all_funds, list):
            print("⚠️ Unexpected fund list format.")
            return []

        equity_funds = [
            fund for fund in all_funds
            if isinstance(fund, dict) and "Equity" in fund.get("schemeName", "")
        ]

        return equity_funds[:count]

    except requests.RequestException as e:
        print(f"❌ Network/API error while fetching funds: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error while fetching funds: {e}")
        return []


# ========== Prompt Builder ==========
def build_prompt(user_data: Dict[str, Any], funds_info: List[Dict[str, Any]]) -> str:
    """
    Create a dynamic prompt for the model.
    """
    user_profile = "\n".join(
        f"{key.replace('_', ' ').title()}: {value}" for key, value in user_data.items()
    )

    fund_list = "\n".join(
        f"- {fund.get('schemeName')}" for fund in funds_info if fund.get("schemeName")
    )

    return f"""
You are a smart, data-driven SIP mutual fund advisor.

Instructions:
- Thoroughly analyze the user's profile and investment goal.
- Carefully study the given mutual funds.
- Only recommend funds with proven growth or strong potential.
- If none are suitable, suggest better alternatives from known categories (like ELSS, large-cap, mid-cap, balanced, flexi-cap).
- Use real financial logic: CAGR, NAV trends, risk category, fund history.
- NEVER suggest funds unless you're confident in their performance and suitability.
- Keep responses concise, structured, and useful.

User Profile:
{user_profile}

Available Mutual Funds:
{fund_list}

Please suggest the 5 best SIP options with detailed reasoning.
""".strip()


# ========== Core SIP Advisor ==========
def recommend_sip_plans(user_data: Dict[str, Any]) -> str:
    """
    Generates SIP recommendations using Groq model based on user profile.
    """
    if not isinstance(user_data, dict) or not user_data:
        return "❌ Invalid or missing user profile data."

    mutual_funds = fetch_top_mutual_funds()

    if not mutual_funds:
        return "⚠️ Unable to fetch mutual fund data. Please try again later."

    prompt = build_prompt(user_data, mutual_funds)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an expert SIP advisor."},
                {"role": "user", "content": prompt}
            ]
        )

        content = completion.choices[0].message.content.strip() if completion.choices else None
        return content or "⚠️ Model returned no content."

    except Exception as e:
        return f"❌ Error generating SIP plan: {str(e)}"


# ========== Example Test ==========
if __name__ == "__main__":
    user_profile = {
        "name": "Nikhil Sharma",
        "age": 34,
        "monthly_income": "₹90,000",
        "risk_profile": "Moderate",
        "goal": "Build ₹25L in 7 years for child’s education",
        "investment_amount": "₹12,000 per month",
        "existing_investments": "₹3L in debt funds",
        "tax_bracket": "30%",
        "location": "Mumbai"
    }

    result = recommend_sip_plans(user_profile)
    print("\n📈 SIP Plan Suggestions:\n")
    print(result)
