import os
import json
from google.adk.agents import Agent
import google.generativeai as genai

# ========== SETUP GEMINI ==========
genai.configure(api_key="sk-moNBXcfMJTnUNQN-LGeu-w")

# ========== DEFINE AGENT ==========
root_agent = Agent(
    model='gemini/gemini-2.0-flash',
    name='agent_goal_planner',
    description='A helpful assistant for user financial goal planning.',
    instruction=(
        "You are a financial goal planner agent. Given a user's current financial details and a goal statement, "
        "analyze their situation and return a realistic, step-by-step plan to help them achieve that goal. "
        "Include savings targets, investment strategy, risk mitigation, and key milestones. Be practical."
    )
)

# ========== SAMPLE FINANCIAL DATA ==========
financial_info = {
    "name": "Sarthak Kulkarni",
    "age": 30,
    "monthly_income": 120000,
    "monthly_expenses": 80000,
    "savings_account_balance": 150000,
    "investments": {
        "mutual_funds": 200000,
        "stocks": 50000,
        "fixed_deposit": 100000
    },
    "debts": {
        "home_loan": 2500000,
        "personal_loan": 300000
    },
    "insurance": {
        "health": "Yes",
        "life": "Yes"
    }
}

# ========== USER GOAL ==========
user_goal = "I want to buy a house worth ₹75 lakhs in 5 years."

# ========== CRAFT PROMPT ==========
prompt = f"""
User Financial Details:
{json.dumps(financial_info, indent=2)}

Goal: {user_goal}

Create a realistic plan for achieving this goal. Break down how much the user needs to save, invest, adjust expenses, or take loans. Be practical, include risks and monthly targets.
"""

# ========== RUN THE AGENT ==========
response = root_agent.run(prompt)

# ========== OUTPUT ==========
print("\n🎯 Financial Goal Plan:\n")
print(response)
