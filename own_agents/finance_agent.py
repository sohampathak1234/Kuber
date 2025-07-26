import os
from dotenv import load_dotenv
from groq import Groq

# ========== Load .env ==========
load_dotenv("own_agents/creds.env")

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("model_name")

if not api_key:
    raise ValueError("❌ Missing GROQ_API_KEY in .env file")
if not model_name:
    raise ValueError("❌ Missing model_name in .env file")

# ========== Initialize Groq Client ==========
client = Groq(api_key=api_key)

# ========== Prompt Template ==========
PROMPT_TEMPLATE = """
You are a financial advisor AI agent. Given the following person's financial details, give realistic and personalized financial insights.
Avoid generic statements. Use financial logic and common planning advice. Mention key ratios like savings rate, debt-to-income, investment advice, etc.

Person Info:
Name: {name}
Age: {age}
Income (monthly): ₹{income}
Monthly Expenses: ₹{expenses}
Loans: {loans}
Savings: ₹{savings}
Investments: {investments}

Give clear bullet points with insights.
"""

# ========== Run Function ==========
def get_financial_insights(name, age, income, expenses, loans, savings, investments):
    prompt = PROMPT_TEMPLATE.format(
        name=name,
        age=age,
        income=income,
        expenses=expenses,
        loans=loans,
        savings=savings,
        investments=investments,
    )

    try:
        chat_completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful and realistic financial advisor."},
                {"role": "user", "content": prompt}
            ]
        )

        print("\n📊 Financial Insights:\n")
        print(chat_completion.choices[0].message.content)

    except Exception as e:
        print(f"❌ Error during completion: {e}")

# ========== Example Usage ==========
if __name__ == "__main__":
    person = {
        "name": "Ravi Verma",
        "age": 32,
        "income": 75000,
        "expenses": 48000,
        "loans": "Car Loan ₹5L (3 yrs left)",
        "savings": 200000,
        "investments": "₹1.2L in Mutual Funds"
    }

    get_financial_insights(**person)
