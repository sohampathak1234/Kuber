import os
from dotenv import load_dotenv
from groq import Groq

# ========== Load Credentials ==========
def load_credentials(env_path="own_agents/creds.env"):
    load_dotenv(env_path)
    api_key = os.getenv("goal_planner_api")
    model_name = os.getenv("model_name")

    if not api_key or not model_name:
        raise ValueError("Missing goal_planner_api or model_name in .env file")

    return api_key, model_name

# ========== Create Groq Client ==========
def create_groq_client(api_key):
    return Groq(api_key=api_key)

# ========== Build Prompt Dynamically ==========
def build_prompt(user_info: dict) -> str:
    goal = user_info.pop("goal", None)
    formatted_fields = "\n".join([f"{key.replace('_', ' ').title()}: {value}" for key, value in user_info.items()])

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
"""
    return prompt

# ========== Generate Response ==========
def generate_goal_plan(user_info: dict, client: Groq, model_name: str) -> str:
    prompt = build_prompt(user_info.copy())  # Avoid mutating original input

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a factual, realistic financial planning assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ========== Universal Entry Point ==========
def run_goal_planner(data: dict, env_path="own_agents/creds.env") -> str:
    api_key, model_name = load_credentials(env_path)
    client = create_groq_client(api_key)
    return generate_goal_plan(data, client, model_name)

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
