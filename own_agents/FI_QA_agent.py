import os
from dotenv import load_dotenv
import google.generativeai as genai

class FactualAgent:
    """
    A robust, factual financial Q&A agent using Gemini API + local knowledge base + dynamic context.
    """

    def __init__(self, env_path="own_agents/creds.env", kb_path=None):
        load_dotenv(env_path)

        self.api_key = os.getenv("FI_QA_gem_api")
        self.model_name = os.getenv("gem_model_name")

        if not self.api_key:
            raise EnvironmentError("❌ Missing 'FI_QA_gem_api' in environment variables.")
        if not self.model_name:
            raise EnvironmentError("❌ Missing 'gem_model_name' in environment variables.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)

        self.kb_path = kb_path
        self.knowledge_base = self._load_knowledge(kb_path) if kb_path else ""

    def _load_knowledge(self, file_path):
        """
        Loads knowledge base content from a text file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return ""
        except Exception as e:
            print(f"❌ Error reading knowledge base: {e}")
            return ""

    def _build_prompt(self, user_input, context=None):
        """
        Builds a strict factual prompt including optional dynamic context.

        Args:
            user_input (str): The user question or statement.
            context (dict): Optional context or variables to inject into the prompt.

        Returns:
            str: The complete prompt.
        """
        context_text = ""
        if context and isinstance(context, dict):
            for key, value in context.items():
                context_text += f"{key}: {value}\n"

        return f"""
You are a highly factual Q&A AI agent for finance-related queries.
You have access to the following verified knowledge base:

Knowledge Base:
\"\"\"{self.knowledge_base.strip()}\"\"\"  

Additional Context:
\"\"\"{context_text.strip()}\"\"\"  

User has asked:
\"{user_input}\"

Respond strictly based on the knowledge base and real, factual internet-based information. Never hallucinate or assume facts. If you don’t know, say you don't know. Be professional, concise and accurate.
"""

    def ask(self, user_input, kb_file=None, **kwargs):
        """
        Answers the user's query with optional new KB and context.

        Args:
            user_input (str): The question or input from user.
            kb_file (str, optional): Alternate KB file for this question.
            **kwargs: Any number of additional key=value context items.

        Returns:
            str: Model's factual response.
        """
        if kb_file:
            self.knowledge_base = self._load_knowledge(kb_file)

        prompt = self._build_prompt(user_input, context=kwargs)

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"❌ Error from Gemini model: {e}"

# ========== Example Usage ==========

# from fi_qa_agent_gemini import FactualAgent
# if __name__ == "__main__":
#     agent = FactualAgent(kb_path="data/FI_money_data.txt")

#     question = "Tell me in short about FI money and its features."
#     context = {
#         "risk_profile": "moderate",
#         "investment_horizon": "5 years",
#         "monthly_investment": "₹10,000"
#     }

#     answer = agent.ask(question, **context)

#     print("\n📌 Answer:")
#     print(answer)
