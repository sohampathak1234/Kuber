import requests
import json

# ========= MCP Config =========
url = "http://localhost:8080/mcp/stream"
session_id = "mcp-session-594e48ea-fea1-40ef-8c52-7552dd9272af"

# ========= Category to Tool Mapping =========


# ========= Ask for Category =========
def call_tools_for_category(category):
    category = category.strip().lower()

    category_tools = {
    "finance": ["fetch_net_worth", "fetch_credit_report", "fetch_bank_transactions"],
    "fiqa": [],
    "goal plan": ["fetch_bank_transactions", "fetch_mf_transactions", "fetch_stock_transactions"],
    "sip": ["fetch_net_worth", "fetch_mf_transactions"],
    "trader": ["fetch_net_worth", "fetch_stock_transactions"]
    }

    if category in category_tools:
        tools_to_call = category_tools[category]
        if not tools_to_call:
            print(f"No tools mapped for category '{category}'.")
            return
        for tool in tools_to_call:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool,
                    "arguments": {}
                }
            }
            headers = {
                "Content-Type": "application/json",
                "Mcp-Session-Id": session_id
            }
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            try:
                resp_json = response.json()
            except Exception:
                resp_json = {"error": "Invalid JSON response", "content": response.text}
            # print(f"\n {tool} Response:\n", json.dumps(resp_json, indent=2))
            # Collect responses
            if 'responses' not in locals():
                responses = []
            responses.append({tool: resp_json})
        return responses
    else:
        print(" Unknown category. Please choose from: finance, fiqa, goal plan, sip, trader.")
        return []

# Example usage:
# category = input(" Enter category (finance, fiqa, goal plan, sip, trader): ")
# responses = call_tools_for_category(category)
# print("Tools called successfully.")
# print(json.dumps(responses, indent=2))
