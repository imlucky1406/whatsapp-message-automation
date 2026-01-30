# 📱 WhatsApp Message sender & Forwarder (WAHA + Google Sheets)

This project allows you to **send & forward the last N WhatsApp messages**  
(**text, image, video, document, voice note**)  
from **one WhatsApp chat (OWNER_CHATID)** to **multiple WhatsApp numbers listed in a Google Sheet**.

It uses **WAHA (WhatsApp HTTP API)**, **Python**, and **Google Sheets**.

---

## 🚀 Features

- ✅ Forward **last 5 WhatsApp messages** (configurable)
- ✅ Supports **all message types**
  - Text
  - Image
  - Video
  - Document (PDF, etc.)
  - Voice note
- ✅ Uses **WAHA forwardMessage** (no re-uploading media)
- ✅ Google Sheet as recipient list
- ✅ Simple configuration
- ✅ Beginner-friendly setup

---

## 🧱 Tech Stack

- Python 3.10+
- WAHA (WhatsApp HTTP API)
- Docker
- Google Sheets API
- gspread
- requests

---

## 🔄 How to Change / Use Your Own Google Sheet

This project is designed so **anyone can use their own Google Sheet** without touching the code.

Follow these steps carefully 👇

---

### ✅ Step 1: Create a New Google Sheet

1. Go to **Google Sheets**
2. Click **Blank** to create a new sheet
3. Rename the sheet (example):

### ✅ Step 2: Set Correct Column Structure

Your Google Sheet **MUST** have these columns in this exact order:

| mobile | name | msg | pdf_link | status |

📌 Notes:
- Mobile number **can be with or without country code**
- Do **NOT** add `@c.us`
- Leave `status` empty — script updates it automatically

---

### ✅ Step 3: Update `GOOGLE_SHEET_NAME` in `config.txt` 

Open `config.txt` and change this line:

```txt
GOOGLE_SHEET_NAME=WhatsApp_Forward_List

---

### ✅ Step 4: Share Google Sheet with Service Account (VERY IMPORTANT)

This step allows the script to **read and update your Google Sheet**.  
If you skip this step, the script will **NOT work**.

---

#### 🔹 1. Open `credentials.json`

Locate the file `credentials.json` in your project folder and open it.

---

#### 🔹 2. Copy `client_email`

Inside `credentials.json`, find the field:

```json
"client_email"
Example:

"client_email": "whatsapp-bot@my-project.iam.gserviceaccount.com"
📌 Copy the entire email address.


####🔹 3. Share the google Sheet
Click the Share button (top-right corner)

Paste the copied client_email

Set permission to Editor

Click Done

✅ The service account now has access to your sheet.

⚠️ Important Notes
You must give Editor access (Viewer is not enough)

The email must be copied exactly (no spaces)

This step is required only once per sheet

❌ Common Mistakes
Mistake	Result
Sheet not shared	Permission denied error
Wrong email	SpreadsheetNotFound
Viewer access only	Update failures
✅ After completing this step, your Google Sheet is fully connected.


---

If you want, next I can:
- Add **screenshots instructions**
- Add **Google Sheet troubleshooting**
- Add **FAQ section**
- Simplify README for beginners

Just tell me 👍

