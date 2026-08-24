import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_gold_signal(bias, entry_zone, stop_loss, tp1, tp2, setup_detail):
    """Sends an ICT XAU/USD signal alert to Telegram."""
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
        "⚠️ *Execution Rules:* Move SL to Breakeven at TP1. Max risk 1%."
    )
    
    payload = {
        "chat_id": CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    # Test sending a real-time Gold setup
    result = send_gold_signal(
        bias="Bullish 🟢",
        setup_detail="15m London Sweep + 1H Fair Value Gap (FVG)",
        entry_zone="2640.00 - 2645.00",
        stop_loss="2625.00",
        tp1="2665.00",
        tp2="2685.00"
    )
    print("Gold signal sent to Telegram!")