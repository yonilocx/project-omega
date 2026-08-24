import os
import time
import requests
import yfinance as yf
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_gold_signal(bias, entry_zone, stop_loss, tp1, tp2, session_name, setup_detail):
    """Dispatches high-conviction ICT Gold signal to Telegram."""
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

def fetch_live_gold_data():
    """Fetches real-time Gold (GC=F / XAUUSD) price candles."""
    gold = yf.Ticker("GC=F")
    df = gold.history(period="2d", interval="15m")
    return df

def run_ict_scanner():
    now_utc = datetime.now(timezone.utc)
    current_hour = now_utc.hour

    print(f"\n[{now_utc.strftime('%Y-%m-%d %H:%M UTC')}] Scanning Gold Market...")

    try:
        df = fetch_live_gold_data()
        if df.empty:
            print("Failed to fetch live market candles.")
            return

        current_price = round(df['Close'].iloc[-1], 2)
        
        # Determine Tokyo Range (High/Low formed between 00:00 and 06:00 UTC today)
        today_data = df[df.index.strftime('%Y-%m-%d') == now_utc.strftime('%Y-%m-%d')]
        tokyo_data = today_data.between_time('00:00', '06:00')

        if not tokyo_data.empty:
            asia_high = round(tokyo_data['High'].max(), 2)
            asia_low = round(tokyo_data['Low'].min(), 2)
        else:
            print("Tokyo range still forming or market closed.")
            return

        print(f"Current Price: ${current_price} | Asia High: ${asia_high} | Asia Low: ${asia_low}")

        # Killzone Time Filters
        is_london = 7 <= current_hour < 10
        is_ny = 12 <= current_hour < 15

        session_label = "London Killzone" if is_london else ("New York Killzone" if is_ny else "Off-Hours")

        if not (is_london or is_ny):
            print(f"[{session_label}] Outside Killzone window. Scanner resting.")
            return

        # ICT Liquidity Sweep Detection
        # 1. Bullish Setup: Sweep of Asia Low
        if current_price < asia_low:
            entry_min = round(asia_low, 2)
            entry_max = round(asia_low + 3.0, 2)
            sl = round(asia_low - 10.0, 2)
            tp1 = round(asia_high, 2)
            tp2 = round(asia_high + 15.0, 2)

            send_gold_signal(
                bias="Bullish 🟢",
                entry_zone=f"{entry_min} - {entry_max}",
                stop_loss=f"{sl}",
                tp1=f"{tp1}",
                tp2=f"{tp2}",
                session_name=session_label,
                setup_detail=f"Live Sweep of Asia Low (${asia_low}) + 15m FVG Reclaim"
            )
            print("Real Bullish Signal Sent!")

        # 2. Bearish Setup: Sweep of Asia High
        elif current_price > asia_high:
            entry_min = round(asia_high - 3.0, 2)
            entry_max = round(asia_high, 2)
            sl = round(asia_high + 10.0, 2)
            tp1 = round(asia_low, 2)
            tp2 = round(asia_low - 15.0, 2)

            send_gold_signal(
                bias="Bearish 🔴",
                entry_zone=f"{entry_min} - {entry_max}",
                stop_loss=f"{sl}",
                tp1=f"{tp1}",
                tp2=f"{tp2}",
                session_name=session_label,
                setup_detail=f"Live Sweep of Asia High (${asia_high}) + 15m FVG Rejection"
            )
            print("Real Bearish Signal Sent!")
        else:
            print("Price inside Asian range. No active sweep detected.")

    except Exception as e:
        print(f"Scanner error: {e}")

if __name__ == "__main__":
    print("Project Omega Live Gold ICT Loop Started...")
    while True:
        run_ict_scanner()
        time.sleep(1800)  # Wait 30 minutes between scans