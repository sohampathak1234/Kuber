import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Tuple


# ========== Load Credentials ==========
def load_credentials(env_path: str = "own_agents/creds.env") -> Tuple[str, str]:
    """
    Load API key and model name from the .env file.

    Returns:
        Tuple containing API key and model name.
    Raises:
        ValueError if required environment variables are missing.
    """
    load_dotenv(env_path, override=False)
    api_key = os.getenv("finance_gem_api")
    model_name = os.getenv("gem_model_name")

    if not api_key:
        raise ValueError("❌ Missing 'finance_gem_api' in .env file.")
    if not model_name:
        raise ValueError("❌ Missing 'gem_model_name' in .env file.")

    return api_key, model_name


# ========== Initialize Gemini Client ==========
def get_gemini_model(api_key: str, model_name: str):
    """
    Initializes the Gemini model client.

    Args:
        api_key: Google Generative AI API Key.
        model_name: Name of the Gemini model.
    Returns:
        A generative model instance.
    """
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


# ========== Build Prompt Dynamically ==========
def build_insight_prompt(user_data: Dict[str, any]) -> str:
    """
    Build a prompt from user financial data.

    Args:
        user_data: A dictionary of user financial information.
    Returns:
        A formatted prompt string for the model.
    """
    if not isinstance(user_data, dict):
        raise ValueError("❌ user_data must be a dictionary.")

    prompt_intro = """
You are a financial advisor AI agent. Given the following person's financial details, give realistic and personalized financial insights.
Avoid generic statements. Use financial logic and common planning advice. Mention key ratios like savings rate, debt-to-income, investment advice, etc.
"""
    user_info = "\n".join([f"{key.replace('_', ' ').title()}: {value}" for key, value in user_data.items()])

    return f"{prompt_intro.strip()}\n\nPerson Info:\n{user_info}\n\nGive clear bullet points with insights."


# ========== Generate Financial Insight ==========
def get_financial_insight(data: Dict[str, any], env_path: str = "own_agents/creds.env") -> str:
    """
    Generate financial insights based on user data.

    Args:
        data: A dictionary containing user's financial data.
        env_path: Path to the environment variable file.
    Returns:
        A factual and actionable financial advice string.
    """
    try:
        api_key, model_name = load_credentials(env_path)
        model = get_gemini_model(api_key, model_name)
        prompt = build_insight_prompt(data)

        response = model.generate_content(prompt)

        return response.text.strip() if response.text else "⚠️ No response from the model."

    except Exception as e:
        return f"❌ Error: {e}"


# ========== Example Use ==========
if __name__ == "__main__":
    test_input = {
        "name": "Ravi Verma",
        "age": 32,
        "income": 75000,
        "expenses": 48000,
        "loans": "Car Loan ₹5L (3 yrs left)",
        "savings": 200000,
        "investments": "₹1.2L in Mutual Funds"
    }

    result = get_financial_insight(test_input)
    print("\n📊 Financial Insights:\n")
    print(result)
