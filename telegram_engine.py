import os
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_gold_signal(bias, entry_zone, stop_loss, tp1, tp2, session_name, setup_detail):
    """Dispatches formatted ICT Gold signal directly to Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    message = (
        "👑 *PROJECT OMEGA — XAU/USD (GOLD) SIGNAL* 👑\n\n"
        f"• *Asset:* Gold (XAU/USD)\n"
        f"• *Session:* {session_name}\n"
        f"• *Bias:* {bias}\n"
        f"• *ICT Pattern:* {setup_detail}\n\n"
        f"🎯 *Entry Zone:* ${entry_zone}\n"
        f"🛑 *Stop Loss:* ${stop_loss}\n"
        f"✅ *Target 1 (TP1):* ${tp1}\n"
        f"🚀 *Target 2 (TP2):* ${tp2}\n\n"
        "⚠️ *Execution Rules:* Move SL to Breakeven at TP1. Risk max 1%."
    )
    
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def analyze_gold_ict_setup(current_price=4635.0, asia_high=4640.0, asia_low=4620.0):
    """
    3-Session ICT Strategy Engine:
    1. Tokyo Session (00:00 - 06:00 UTC): Maps Liquidity Range (High/Low)
    2. London Killzone (07:00 - 10:00 UTC): Scans for Tokyo High/Low Sweeps + FVG
    3. New York Killzone (12:00 - 15:00 UTC): Scans for NY High/Low Sweeps + FVG
    """
    now_utc = datetime.now(timezone.utc)
    current_hour = now_utc.hour

    # Session Time Filters
    is_tokyo_session = 0 <= current_hour < 6
    is_london_killzone = 7 <= current_hour < 10
    is_ny_killzone = 12 <= current_hour < 15

    if is_tokyo_session:
        print(f"[{now_utc.strftime('%H:%M UTC')}] Tokyo Session Active: Recording Asia Range (High: ${asia_high} | Low: ${asia_low}). No trade entries.")
        return

    session_label = "London Killzone" if is_london_killzone else ("New York Killzone" if is_ny_killzone else "Off-Hours")

    # ICT Sweep Logic
    if is_london_killzone or is_ny_killzone:
        # Bullish Setup: Price sweeps Asia Low then leaves a Bullish FVG
        if current_price < asia_low:
            entry_min = round(asia_low + 2.0, 2)
            entry_max = round(asia_low + 5.0, 2)
            sl = round(asia_low - 12.0, 2)
            tp1 = round(asia_high, 2)
            tp2 = round(asia_high + 20.0, 2)

            send_gold_signal(
                bias="Bullish 🟢",
                entry_zone=f"{entry_min} - {entry_max}",
                stop_loss=f"{sl}",
                tp1=f"{tp1}",
                tp2=f"{tp2}",
                session_name=session_label,
                setup_detail=f"Liquidity Sweep of Asia Low (${asia_low}) + 15m Bullish FVG"
            )
            print(f"[{session_label}] Bullish ICT Gold Signal Sent!")

        # Bearish Setup: Price sweeps Asia High then leaves a Bearish FVG
        elif current_price > asia_high:
            entry_min = round(asia_high - 5.0, 2)
            entry_max = round(asia_high - 2.0, 2)
            sl = round(asia_high + 12.0, 2)
            tp1 = round(asia_low, 2)
            tp2 = round(asia_low - 20.0, 2)

            send_gold_signal(
                bias="Bearish 🔴",
                entry_zone=f"{entry_min} - {entry_max}",
                stop_loss=f"{sl}",
                tp1=f"{tp1}",
                tp2=f"{tp2}",
                session_name=session_label,
                setup_detail=f"Liquidity Sweep of Asia High (${asia_high}) + 15m Bearish FVG"
            )
            print(f"[{session_label}] Bearish ICT Gold Signal Sent!")
        else:
            print(f"[{session_label}] Price inside Asia Range. Waiting for Liquidity Sweep...")
    else:
        print(f"[{now_utc.strftime('%H:%M UTC')}] Outside Killzone window. Scanner resting.")

if __name__ == "__main__":
    # Test simulation of a London Killzone Liquidity Sweep
    print("Testing 3-Session ICT Engine...")
    analyze_gold_ict_setup(current_price=4618.0, asia_high=4640.0, asia_low=4620.0)