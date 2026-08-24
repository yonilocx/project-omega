import os
import time
from datetime import datetime, timezone
import yfinance as yf
import requests

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Keep your token here
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"      # Keep your chat ID here

ACCOUNT_BALANCE = 100.0   # $100 Account
RISK_PERCENT = 0.02       # 2% Risk = $2.00 Max Risk per trade

# ---------------------------------------------------------
# TELEGRAM NOTIFIER
# ---------------------------------------------------------
def send_telegram_message(message):
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"[Telegram Alert Output]:\n{message}\n")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def send_gold_signal(direction, entry_min, entry_max, sl, tp1, tp2):
    sl_distance = abs(entry_min - sl)
    
    # 2% Risk Calculation ($2.00)
    risk_amount = ACCOUNT_BALANCE * RISK_PERCENT
    calculated_lots = round(risk_amount / (sl_distance * 100), 2)
    lot_size = max(0.01, calculated_lots)

    msg = (
        f"🚨 *PROJECT OMEGA: HIGH-CONVICTION ICT SIGNAL* 🚨\n\n"
        f"📊 *Asset:* GOLD (XAU/USD)\n"
        f"📈 *Direction:* {direction}\n\n"
        f"🎯 *Entry Zone:* ${entry_min:.2f} - ${entry_max:.2f}\n"
        f"🛑 *Stop Loss:* ${sl:.2f}\n"
        f"🏁 *Take Profit 1 (1:2):* ${tp1:.2f}\n"
        f"🚀 *Take Profit 2 (Liquidity):* ${tp2:.2f}\n\n"
        f"🛡️ *Risk Profile (Moderate):*\n"
        f"• Risk Amount: ${risk_amount:.2f} (2%)\n"
        f"• Recommended Lot Size: `{lot_size}`\n\n"
        f"⏳ *Strategy:* Liquidity Sweep + 15m Displacement FVG"
    )
    send_telegram_message(msg)

# ---------------------------------------------------------
# MARKET SCANNER & TIME FILTERS
# ---------------------------------------------------------
def run_precision_ict_scanner():
    print("Project Omega Live Gold ICT Loop Started...\n")
    
    while True:
        now_utc = datetime.now(timezone.utc)
        current_hour = now_utc.hour
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M UTC")

        # Killzone Filter (London: 07:00-10:00 UTC | NY: 12:00-15:00 UTC)
        in_london = 7 <= current_hour < 10
        in_ny = 12 <= current_hour < 15

        print(f"[{timestamp}] Scanning Gold Market...")

        if not (in_london or in_ny):
            print("[Off-Hours] Outside Killzone window. Scanner resting.\n")
            time.sleep(1800)
            continue

        try:
            # Fetch Gold Data
            ticker = yf.Ticker("GC=F")
            df = ticker.history(period="2d", interval="15m")

            if df.empty:
                print("Warning: No data fetched from yfinance.")
                time.sleep(1800)
                continue

            current_price = df['Close'].iloc[-1]
            asia_high = df['High'].iloc[:24].max()
            asia_low = df['Low'].iloc[:24].min()

            print(f"Current Price: ${current_price:.1f} | Asia High: ${asia_high:.1f} | Asia Low: ${asia_low:.1f}")

            # ICT Setup Condition Evaluation
            if current_price > asia_high:
                print("🔥 Asia High Swept! Evaluating Short FVG...")
                # Add setup triggering logic here
            elif current_price < asia_low:
                print("🔥 Asia Low Swept! Evaluating Long FVG...")
                # Add setup triggering logic here
            else:
                print("Price inside Asian range. No active sweep detected.\n")

        except Exception as e:
            print(f"Error fetching data: {e}\n")

        # Sleep for 30 minutes before next scan
        time.sleep(1800)

# ---------------------------------------------------------
# EXECUTION ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    run_precision_ict_scanner()