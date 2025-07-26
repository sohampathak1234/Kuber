import os
from dotenv import load_dotenv
from groq import Groq
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
    api_key = os.getenv("GROQ_API_KEY")
    model_name = os.getenv("model_name")

    if not api_key:
        raise ValueError("❌ Missing GROQ_API_KEY in .env file")
    if not model_name:
        raise ValueError("❌ Missing model_name in .env file")

    return api_key, model_name


# ========== Initialize Client ==========
def get_groq_client(api_key: str) -> Groq:
    """
    Initialize and return a Groq client.

    Args:
        api_key: Your Groq API key.
    Returns:
        An initialized Groq client instance.
    """
    return Groq(api_key=api_key)


# ========== Build Prompt Dynamically ==========
def build_insight_prompt(user_data: Dict[str, any]) -> str:
    """
    Build a prompt from user financial data.

    Args:
        user_data: A dictionary of user financial information.
    Returns:
        A formatted prompt string for the model.
    Raises:
        ValueError if user_data is not a dictionary.
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
        client = get_groq_client(api_key)
        prompt = build_insight_prompt(data)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful and realistic financial advisor."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip() if response.choices else "⚠️ No response from the model."

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
