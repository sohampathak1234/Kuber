import os
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# Load environment variables
load_dotenv("own_agents/creds.env")
MODEL_NAME = os.getenv("model_name")  # llama3-70b-8192
API_KEY = os.getenv("sending_email_api")  # groq key

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]
TOKEN_FILE = 'own_agents/token.json'

# ========== Step 1: Authenticate Gmail ==========
def authenticate_gmail():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build('gmail', 'v1', credentials=creds)
    return service

# ========== Step 2: Generate Email Body using Groq + OpenAI Client ==========
def generate_email_reply(subject, body, category, llm_output: dict) -> str:
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )

    prompt = f"""
You are a smart assistant. Read the email subject, body, and its context category. Use the output provided by the previous LLM agent to generate a clear, polite and complete response email.

Email Subject: {subject}
Email Body:
{body}

Email Category: {category}
Previous Agent Output:
{json.dumps(llm_output, indent=2)}

Now draft an email reply for the user.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant drafting polite email replies."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()

# ========== Step 3: Send Email ==========
def send_email(to_email: str, subject: str, reply_body: str):
    service = authenticate_gmail()
    message = MIMEText(reply_body)
    message['to'] = to_email
    message['from'] = "dizboardmanager@gmail.com"
    message['subject'] = f"RE: {subject}"

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw_message}

    send_result = service.users().messages().send(userId='me', body=message_body).execute()
    print(f"✅ Email sent to {to_email} with Message ID: {send_result['id']}")

# ========== Step 4: Orchestrated Call ==========
def generate_and_send_reply(to_email: str, subject: str, body: str, category: str, llm_output: dict):
    print("💡 Generating reply from LLM...")
    reply_text = generate_email_reply(subject, body, category, llm_output)
    print("✉️ Sending email...")
    send_email(to_email, subject, reply_text)

# ========== Example ==========
if __name__ == "__main__":
    to_email = "dizboardmanager@gmail.com"
    subject = "Need help with SIP planning"
    body = "Hi team, I would like to know how much I should invest in SIP to reach my goal of buying a car in 3 years."
    category = "SIP Advice"
    llm_output = {
        "recommendation": "Invest ₹10,000 monthly in a mid-cap mutual fund with ~12% expected return.",
        "target_goal": "Car purchase in 3 years",
        "estimated_return": "₹4.3L - ₹4.5L"
    }

    generate_and_send_reply(to_email, subject, body, category, llm_output)
