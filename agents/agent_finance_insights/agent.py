import os
import json
import asyncio
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# Load credentials
load_dotenv(dotenv_path="agents/agent_finance_insights/.env")

MODEL_NAME = "gemini-pro"  # 

class FinanceAgent:
    def __init__(self):
        self.agent = Agent(
            model=LiteLlm(model=MODEL_NAME),
            name="finance_insight_agent",
            description="Analyzes personal financial data and provides actionable insights.",
            instruction=(
                "You are a personal financial advisor AI. "
                "Given structured data (income, expenses, investments, debts), "
                "calculate savings rate, debt ratios, investment diversification, "
                "and provide realistic, actionable suggestions."
            )
        )

class FinanceAgentRunner:
    def __init__(self, agent: FinanceAgent):
        self.session_service = InMemorySessionService()
        self.runner = InMemoryRunner(agent=agent.agent, session_service=self.session_service)

    async def run_insights(self, user_data: dict) -> str:
        # Create a session
        await self.session_service.create_session(
            app_name="finance_insight_app",
            user_id="user1",
            session_id="session1"
        )

        # Build the user prompt as Content
        payload = {
            "user_financial_data": user_data,
            "analysis_request": "Analyze and give clear financial insights."
        }
        content = Content(role="user", parts=[Part(text=json.dumps(payload, indent=2))])

        # Invoke agent
        response = ""
        async for event in self.runner.run_async(
            user_id="user1", session_id="session1", new_message=content
        ):
            if event.content and event.content.parts:
                response += event.content.parts[0].text

        return response

if __name__ == "__main__":
    sample_data = {
        "name": "Rahul Verma",
        "age": 35,
        "income": 1800000,
        "expenses": {
            "rent": 360000,
            "groceries": 144000,
            "transport": 72000,
            "entertainment": 108000,
            "utilities": 48000,
            "others": 60000
        },
        "investments": {
            "mutual_funds": 250000,
            "stocks": 200000,
            "fixed_deposit": 100000
        },
        "debts": {
            "credit_card": 40000,
            "home_loan": 300000
        }
    }

    agent = FinanceAgent()
    runner = FinanceAgentRunner(agent)
    insights = asyncio.run(runner.run_insights(sample_data))

    print("\n📊 Financial Insights for Rahul Verma:\n")
    print(insights)
