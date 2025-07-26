import os
from typing import Tuple, Dict
from dotenv import load_dotenv
import google.generativeai as genai


# ========== Load Credentials ==========
def load_credentials(env_path: str = "own_agents/creds.env") -> Tuple[str, str]:
    """
    Load the API key and model name from the .env file.
    """
    load_dotenv(env_path)
    api_key = os.getenv("goal_planner_gemini_api")
    model_name = os.getenv("gem_model_name")

    if not api_key:
        raise ValueError("❌ Missing 'goal_planner_gemini_api' in .env file")
    if not model_name:
        raise ValueError("❌ Missing 'gem_model_name' in .env file")

    return api_key, model_name


# ========== Create Gemini Client ==========
def create_gemini_model(api_key: str, model_name: str):
    """
    Initialize the Gemini model client.
    """
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


# ========== Build Prompt Dynamically ==========
def build_prompt(user_info: Dict[str, any]) -> str:
    """
    Construct a prompt for financial planning based on user data.
    """
    if not isinstance(user_info, dict):
        raise ValueError("❌ user_info must be a dictionary")

    user_info = user_info.copy()  # Avoid mutating original input
    goal = user_info.pop("goal", None)
    formatted_fields = "\n".join(
        f"{key.replace('_', ' ').title()}: {value}" for key, value in user_info.items()
    )

    prompt = f"""
You are a financial goal planner AI assistant. Based on the user's financial situation and their goal, generate a realistic financial plan.

Rules:
- Avoid hallucinations or generic advice.
- Use real financial logic.
- Suggest practical steps based on the user's income, expenses, and timeline.

User Financial Info:
{formatted_fields}

Goal Statement:
"{goal or 'No specific goal mentioned.'}"

Now suggest a realistic, step-by-step financial plan to help the user achieve the goal efficiently.
""".strip()

    return prompt


# ========== Generate Response ==========
def generate_goal_plan(user_info: Dict[str, any], model) -> str:
    """
    Generate a step-by-step financial plan using Gemini.
    """
    try:
        prompt = build_prompt(user_info)

        response = model.generate_content(
            prompt
        )

        return response.text.strip() if response.text else "⚠️ No meaningful response received from the model."

    except Exception as e:
        return f"❌ Error during generation: {str(e)}"


# ========== Universal Entry Point ==========
def run_goal_planner(data: Dict[str, any], env_path: str = "own_agents/creds.env") -> str:
    """
    Universal entry point to trigger the financial goal planning logic.
    """
    api_key, model_name = load_credentials(env_path)
    model = create_gemini_model(api_key, model_name)
    return generate_goal_plan(data, model)


# ========== Example Test ==========
if __name__ == "__main__":
    example_input = {
        "name": "Ankita Mehta",
        "age": 30,
        "income": 70000,
        "expenses": 40000,
        "savings": 250000,
        "investments": "₹1.5L in FDs, ₹80K in mutual funds",
        "loans": "None",
        "goal": "I want to go on a Europe trip worth ₹4.5 lakhs within 18 months."
    }

    result = run_goal_planner(example_input)
    print("\n🧠 Financial Goal Plan:\n")
    print(result)
