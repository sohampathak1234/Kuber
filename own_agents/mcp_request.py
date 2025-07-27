import requests
import json

# ========= MCP Config =========
url = "http://localhost:8080/mcp/stream"
session_id = "mcp-session-594e48ea-fea1-40ef-8c52-7552dd9272af"

# ========= Category to Tool Mapping =========
category_tools = {
    "finance": ["fetch_net_worth", "fetch_credit_report", "fetch_bank_transactions"],
    "fiqa": [],
    "goal plan": ["fetch_bank_transactions", "fetch_mf_transactions", "fetch_stock_transactions"],
    "sip": ["fetch_net_worth", "fetch_mf_transactions"],
    "trader": ["fetch_net_worth", "fetch_stock_transactions"]
}

# ========= Ask for Category =========
category = input("🧠 Enter category (finance, fiqa, goal plan, sip, trader): ").strip().lower()

if category in category_tools:
    tools_to_call = category_tools[category]
    if not tools_to_call:
        print(f"No tools mapped for category '{category}'.")
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
        print(f"\n✅ {tool} Response:\n", json.dumps(response.json(), indent=2))
else:
    print(" Unknown category. Please choose from: finance, fiqa, goal plan, sip, trader.")
