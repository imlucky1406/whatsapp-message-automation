import gspread
import requests
import time
import os
from google.oauth2 import service_account

# ==============================
# Load Config from config.txt
# ==============================
def load_config(filename="config.txt"):
    config = {}
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


config = load_config()

GOOGLE_SHEET_NAME = config["GOOGLE_SHEET_NAME"]
WAHA_URL = config["WAHA_URL"]
WAHA_API_KEY = config["WAHA_API_KEY"]
SESSION = config["SESSION"]
OWNER_CHATID = config["OWNER_CHATID"]
limit = config["LIMIT"]


COUNTRY_CODE = config["COUNTRY_CODE"]
DELAY_SECONDS = 5


# ------- Credentials (ENV VAR) --------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(BASE_DIR, "credentials.json")

if not os.path.exists(credentials_path):
    raise Exception(f"credentials.json not found at {credentials_path}")

creds = service_account.Credentials.from_service_account_file(
    credentials_path,
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1
rows = sheet.get_all_values()

# --------- header -----
WAHA_HEADERS = {
    "X-Api-Key": WAHA_API_KEY,
    "Content-Type": "application/json"
}


# --------- send text -----
def send_text(chat_id, text):
    response = requests.post(
        f"{WAHA_URL}/api/sendText",
        json={
            "session": SESSION,
            "chatId": chat_id,
            "text": text
        },
        headers=WAHA_HEADERS,
        timeout=30
    )
    response.raise_for_status()



#--------- forward one msg -----
def forward_message(target_chat_id, message_id):
    response = requests.post(
        f"{WAHA_URL}/api/forwardMessage",
        headers=WAHA_HEADERS,
        json={
            "session": SESSION,
            "chatId": target_chat_id,
            "messageId": message_id
        },
        timeout=30
    )
    response.raise_for_status()

#--------- get last msgs -----
def get_last_messages(chat_id, limit=5):
    url = f"{WAHA_URL}/api/{SESSION}/chats/{chat_id}/messages"

    params = {
        "limit": limit,
        "sortOrder": "desc",      # newest first
        "downloadMedia": False    # faster, still forwards media
    }

    response = requests.get(
        url,
        headers=WAHA_HEADERS,
        params=params,
        timeout=30
    )
    response.raise_for_status()

    return response.json()



#--------- forward last msg -----
def forward_last_messages(owner_chat_id, target_chat_id, count=5):
    messages = get_last_messages(owner_chat_id, limit=count)

    if not messages:
        print("⚠ No messages to forward")
        return

    # Reverse so order stays same as WhatsApp (old → new)
    messages = list(reversed(messages))

    for msg in messages:
        msg_id = msg.get("id")
        msg_type = msg.get("type")

        if not msg_id:
            continue

        print(f"➡ Forwarding {msg_type} message")
        forward_message(target_chat_id, msg_id)
        time.sleep(1)   # avoid spam / rate limit


#--------- send pdf -----
def send_pdf(chat_id, pdf_url):
    response = requests.post(
        f"{WAHA_URL}/api/sendFile",
        json={
            "session": SESSION,
            "chatId": chat_id,
            "url": pdf_url,
            "filename": "Document.pdf"
        },
        headers=WAHA_HEADERS,
        timeout=30
    )
    response.raise_for_status()

# -------- main -------
for i in range(1, len(rows)):
    try:
        mobile, name, msg, pdf_link, status = rows[i]
    except ValueError:
        print(f"⚠ Skipping row {i + 1}: invalid column count")
        continue

    if status.strip().lower() == "sent":
        print(f"Row {i + 1}: already sent")
        continue

    chat_id = f"{COUNTRY_CODE}{mobile}@c.us"
    message = msg.replace("{full name}", name)

    try:
        print(f"📤 Sending to {chat_id}")

        send_text(chat_id, message)
        time.sleep(DELAY_SECONDS)

        # Uncomment if PDF required
        # send_pdf(chat_id, pdf_link)
        # time.sleep(DELAY_SECONDS)

        print(f"📤 Forwarding last 5 messages to {chat_id}")

        forward_last_messages(
            OWNER_CHATID,
            chat_id,
            count=5
        )

        sheet.update_cell(i + 1, 5, "sent")
        print("Sent successfully")

    except Exception as error:
        sheet.update_cell(i + 1, 5, "failed")
        print("Failed:", error)
        
print("Script completed")
