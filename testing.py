import requests
import json

url = "http://localhost:8080/mcp/stream"

payload = json.dumps({
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "fetch_net_worth",
    "arguments": {}
  }
})
headers = {
  'Content-Type': 'application/json',
  'Mcp-Session-Id': 'mcp-session-594e48ea-fea1-40ef-8c52-7552dd9272af'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)