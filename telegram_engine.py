import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_gold_signal(bias, entry_zone, stop_loss, tp1, tp2, setup_detail):
    """Sends a dedicated ICT XAU/USD (Gold) signal alert to Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    message = (
        "👑 *PROJECT OMEGA — XAU/USD (GOLD) SIGNAL* 👑\n\n"
        f"• *Asset:* Gold (XAU/USD)\n"
        f"• *Bias:* {bias}\n"
        f"• *ICT Setup:* {setup_detail}\n\n"
        f"🎯 *Entry Zone:* ${entry_zone}\n"
        f"🛑 *Stop Loss:* ${stop_loss}\n"
        f"✅ *Target 1 (TP1):* ${tp1}\n"
        f"🚀 *Target 2 (TP2):* ${tp2}\n\n"
        "⚠️ *Execution Rules:* Risk max 1%. Move SL to Breakeven at TP1."
    )
    
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    return response.json()

def send_gold_chart(image_path, caption=""):
    """Sends a Gold chart snapshot alongside the alert."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}
            requests.post(url, data=data, files=files)
            print("Gold chart successfully sent!")
    else:
        print("Chart image path not found.")

if __name__ == "__main__":
    # Test dispatching a live XAU/USD signal reflecting current gold pricing (~$4,630s)
    result = send_gold_signal(
        bias="Bullish 🟢",
        setup_detail="15m London Sweep + 1H Fair Value Gap (FVG)",
        entry_zone="4620.00 - 4625.00",
        stop_loss="4605.00",
        tp1="4645.00",
        tp2="4665.00"
    )
    print("XAU/USD signal sent to Telegram!")