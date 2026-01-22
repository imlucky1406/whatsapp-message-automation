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

COUNTRY_CODE = 91
DELAY_SECONDS = 5


# ------- Credentials (ENV VAR) --------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not credentials_path:
    raise Exception(
        "GOOGLE_APPLICATION_CREDENTIALS not set.\n"
        "Windows:\n"
        "  setx GOOGLE_APPLICATION_CREDENTIALS \"C:\\Users\\lucky\\secrets\\credentials.json\"\n"
        "Linux/Mac:\n"
        "  export GOOGLE_APPLICATION_CREDENTIALS=\"/path/to/credentials.json\""
    )

creds = service_account.Credentials.from_service_account_file(
    credentials_path,
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1
rows = sheet.get_all_values()

# --------- send text-----
def send_text(chat_id, text):
    response = requests.post(
        f"{WAHA_URL}/api/sendText",
        json={
            "session": SESSION,
            "chatId": chat_id,
            "text": text
        },
        headers={
            "X-Api-Key": WAHA_API_KEY,
            "Content-Type": "application/json"
        },
        timeout=30
    )
    response.raise_for_status()

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
        headers={
            "X-Api-Key": WAHA_API_KEY,
            "Content-Type": "application/json"
        },
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

        sheet.update_cell(i + 1, 5, "sent")
        print("Sent successfully")

    except Exception as error:
        sheet.update_cell(i + 1, 5, "failed")
        print("Failed:", error)

# ==============================
print("Script completed")
