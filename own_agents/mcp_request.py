import requests
import json

# ========= MCP Config =========
url = "http://localhost:8080/mcp/stream"
session_id = "mcp-session-594e48ea-fea1-40ef-8c52-7552dd9272af"

# ========= Tool List with Keywords =========
tool_keywords = {
    "fetch_net_worth": ["net worth", "total assets", "portfolio", "wealth"],
    "fetch_credit_report": ["credit score", "credit report", "cibil", "loans", "credit card"],
    "fetch_epf_details": ["epf", "provident fund", "pf balance"],
    "fetch_mf_transactions": ["mutual fund", "mf", "sip", "investment"],
    "fetch_bank_transactions": ["bank statement", "transactions", "account history"],
    "fetch_stock_transactions": ["stock", "shares", "nifty", "indian stock"]
}

# ========= Ask for User Query =========
user_input = input("🧠 What financial data do you want to fetch? ").lower()

# ========= Match Tool Based on Input =========
matched_tool = None
for tool, keywords in tool_keywords.items():
    if any(keyword in user_input for keyword in keywords):
        matched_tool = tool
        break

if matched_tool:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": matched_tool,
            "arguments": {}
        }
    }

    headers = {
        "Content-Type": "application/json",
        "Mcp-Session-Id": session_id
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print("✅ Response:\n", json.dumps(response.json(), indent=2))
else:
    print("❌ Sorry, couldn't understand what tool to call based on your input.")
