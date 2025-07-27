import json
import importlib

# ========== Step 1: Fetch Email ==========
def fetch_email():
    from own_agents import email_fetching
    email_fetching.main()  # should create temp_email.json
    print("[1/6] ✅ Email fetched and stored in temp_email.json")


# ========== Step 2: Categorize Email ==========
def categorize_email():
    from own_agents import categorizing_agent

    result = categorizing_agent.main()  # expected to return: { name, phone, email, category }
    print(f"[2/6] ✅ Email categorized as: {result.get('category')}")
    return result


# ========== Step 3: Fetch FI Data Based on Category ==========
def fetch_fi_data(category, metadata):
    from FI_things import FI_fetcher

    fi_data = FI_fetcher.fetch(category=category, metadata=metadata)
    print(f"[3/6] ✅ FI data fetched for category '{category}'")
    return fi_data


# ========== Step 4: Route to Specific Agent ==========
def call_agent(category, input_data):
    category_to_agent = {
        "FI_QA": "FI_QA_agent",
        "Finance": "finance_agent",
        "Goal_Planning": "goal_planner_agent",
        "SIP_Advisor": "sip_advisor_agent",
        "Trade_Executor": "trade_executor_agent",
    }

    agent_module_name = category_to_agent.get(category)
    if not agent_module_name:
        print(f"[4/6] ⚠️ No agent for category: {category}")
        return None

    module_path = f"own_agents.{agent_module_name}"
    agent_module = importlib.import_module(module_path)
    output = agent_module.main(input_data)
    print(f"[4/6] ✅ Agent '{agent_module_name}' executed")
    return output


# ========== Step 5: Send Email Back ==========
def send_response_email(recipient_email, message):
    from own_agents import send_email
    send_email.send(recipient_email, message)
    print(f"[5/6] ✅ Response sent to: {recipient_email}")


# ========== Main Orchestration ==========
def main():
    fetch_email()

    with open("temp_email.json", "r") as f:
        email_data = json.load(f)

    result = categorize_email()
    category = result.get("category")
    recipient_email = result.get("email")

    if category == "Non-standard":
        print("[X] 🚫 Phishing/Non-standard email detected. Skipping.")
        return

    fi_data = fetch_fi_data(category, metadata=result)
    agent_output = call_agent(category, input_data=fi_data)

    if agent_output:
        send_response_email(recipient_email, agent_output)
    else:
        print("[!] ⚠️ No response generated. Skipping email reply.")


if __name__ == "__main__":
    main()
