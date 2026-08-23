import sys
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_alert(message):
    """
    Sends a formatted alert message to your private Telegram chat.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        return {
            "success": False, 
            "error": "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env file."
        }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        res_data = response.json()
        if res_data.get("ok"):
            return {"success": True, "message": "Telegram alert sent successfully."}
        else:
            return {"success": False, "error": res_data.get("description")}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python notify.py '<message>'"}))
        sys.exit(1)

    alert_msg = sys.argv[1]
    result = send_telegram_alert(alert_msg)
    print(json.dumps(result, indent=2))
