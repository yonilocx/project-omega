import os
import json
import requests
from dotenv import load_dotenv
from logger import log_ict_trade

# Load local environment variables
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing in .env")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending alert: {e}")

def run_ict_scanner():
    print("Scanning Gold (XAUUSD) for 15M ICT Setups...")
    
    # Placeholder values for live engine execution logic
    # Replace these variable assignments with your live technical indicators/sweeps logic
    signal_found = False  # Set to True when BOS/FVG/Sweep condition triggers
    
    if signal_found:
        signal_type = "BUY"
        entry_price = 2648.25
        setup_name = "15M Asian Sweep + FVG"
        tp_level = 2660.00
        sl_level = 2640.00
        
        # 1. Format and send Telegram Alert
        alert_msg = f"?? *PROJECT OMEGA SIGNAL*\n\n" \
                    f"Asset: Gold (XAUUSD)\n" \
                    f"Type: {signal_type}\n" \
                    f"Entry: ${entry_price}\n" \
                    f"Setup: {setup_name}\n" \
                    f"TP: ${tp_level} | SL: ${sl_level}"
        send_telegram_alert(alert_msg)
        
        # 2. Append trade log & sync to GitHub Pages
        log_ict_trade(signal_type, entry_price, setup_name, tp_level, sl_level)
    else:
        print("Scan complete. No setup detected.")

if __name__ == "__main__":
    run_ict_scanner()

