import os
import base64
from typing import Optional, Dict
from email import message_from_bytes
from email.message import Message

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ========== LOAD ENV ==========
load_dotenv("own_agents/creds.env")  

# ========== CONFIGURATION ==========
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_FILE = 'own_agents/token.json'

CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise EnvironmentError("❌ GMAIL_CLIENT_ID or GMAIL_CLIENT_SECRET not found in .env file.")


# ========== AUTHENTICATION ==========

def authenticate_gmail() -> Optional[object]:
    """Authenticate Gmail API using client ID/secret from environment."""
    try:
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": CLIENT_ID,
                            "client_secret": CLIENT_SECRET,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                        }
                    },
                    SCOPES
                )
                creds = flow.run_local_server(port=0)
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    except Exception as e:
        print(f"❌ Gmail authentication failed: {e}")
        return None


# ========== EMAIL UTILITIES ==========

def extract_plain_text_body(msg: Message) -> str:
    """Extract plain text from MIME message."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain' and not part.get_filename():
                try:
                    return part.get_payload(decode=True).decode()
                except Exception:
                    continue
    else:
        try:
            return msg.get_payload(decode=True).decode()
        except Exception:
            return ''
    return ''


def fetch_latest_unread_email(service) -> Optional[Dict[str, str]]:
    """Fetch most recent unread email and mark it as read."""
    try:
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=1
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            print("📭 No unread emails found.")
            return None

        msg_id = messages[0]['id']
        msg_raw = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        raw_data = base64.urlsafe_b64decode(msg_raw['raw'].encode('ASCII'))
        mime_msg: Message = message_from_bytes(raw_data)

        subject = mime_msg.get('Subject', '(No Subject)')
        body = extract_plain_text_body(mime_msg)

        # Mark as read
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

        return {'subject': subject, 'body': body}

    except HttpError as e:
        print(f"❌ Gmail API error: {e}")
    except Exception as e:
        print(f"❌ Failed to fetch email: {e}")
    return None


# ========== ENTRY FUNCTION ==========

def get_latest_unread_email() -> Optional[Dict[str, str]]:
    """Main reusable function to fetch and return unread email."""
    service = authenticate_gmail()
    if not service:
        return None
    return fetch_latest_unread_email(service)


# ========== LOCAL TEST ==========
if __name__ == '__main__':
    email_data = get_latest_unread_email()
    if email_data:
        print(f"\n📧 Subject: {email_data['subject']}\n\n📩 Body:\n{email_data['body']}")
    else:
        print("📭 No unread emails found or an error occurred.")
