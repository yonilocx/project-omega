import os
import time
from datetime import datetime, timezone
import yfinance as yf
import requests
import matplotlib.pyplot as plt
import mplfinance as mpf

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"

ACCOUNT_BALANCE = 100.0   # $100 Account
RISK_PERCENT = 0.02       # 2% Risk = $2.00 Max Risk per trade

# ---------------------------------------------------------
# CHART GENERATOR & TELEGRAM SENDER
# ---------------------------------------------------------
def generate_and_send_chart(df, direction, entry_min, entry_max, sl, tp1, tp2, asia_high, asia_low):
    chart_filename = "ict_gold_setup.png"
    
    # Plot recent 30 candles
    recent_df = df.tail(30).copy()

    # Define color overlays for levels
    hlines = [asia_high, asia_low, entry_min, sl, tp1, tp2]
    colors = ['gray', 'gray', 'blue', 'red', 'green', 'darkgreen']
    styles = ['--', '--', '-', '-', '-', '-']

    # Generate Chart Image
    fig, ax = plt.subplots(figsize=(10, 6))
    mpf.plot(
        recent_df,
        type='candle',
        style='charles',
        title=f"XAU/USD 15m - ICT {direction} Setup",
        ylabel='Price ($)',
        hlines=dict(hlines=hlines, colors=colors, linestyle=styles, linewidths=1.5),
        savefig=chart_filename
    )
    plt.close('all')

    # Send Chart Image to Telegram
    if TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(chart_filename, 'rb') as photo:
            payload = {'chat_id': TELEGRAM_CHAT_ID, 'caption': f"📊 *ICT Chart Snapshot - XAU/USD ({direction})*"}
            try:
                requests.post(url, data=payload, files={'photo': photo}, timeout=15)
            except Exception as e:
                print(f"Failed to send chart image: {e}")

    # Clean up local image file
    if os.path.exists(chart_filename):
        os.remove(chart_filename)

def send_gold_signal(df, direction, entry_min, entry_max, sl, tp1, tp2, asia_high, asia_low):
    sl_distance = abs(entry_min - sl)
    risk_amount = ACCOUNT_BALANCE * RISK_PERCENT
    calculated_lots = round(risk_amount / (sl_distance * 100), 2)
    lot_size = max(0.01, calculated_lots)

    # First send the chart snapshot
    generate_and_send_chart(df, direction, entry_min, entry_max, sl, tp1, tp2, asia_high, asia_low)

    # Then send the signal breakdown text
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
    
    if TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Failed to send text signal: {e}")

# ---------------------------------------------------------
# MARKET SCANNER & TIME FILTERS
# ---------------------------------------------------------
def run_precision_ict_scanner():
    print("Project Omega Live Gold ICT Loop Started...\n")
    
    while True:
        now_utc = datetime.now(timezone.utc)
        current_hour = now_utc.hour
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M UTC")

        in_london = 7 <= current_hour < 10
        in_ny = 12 <= current_hour < 15

        print(f"[{timestamp}] Scanning Gold Market...")

        if not (in_london or in_ny):
            print("[Off-Hours] Outside Killzone window. Scanner resting.\n")
            time.sleep(1800)
            continue

        try:
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

            if current_price > asia_high:
                print("🔥 Asia High Swept! Evaluating Short FVG...")
            elif current_price < asia_low:
                print("🔥 Asia Low Swept! Evaluating Long FVG...")
            else:
                print("Price inside Asian range. No active sweep detected.\n")

        except Exception as e:
            print(f"Error fetching data: {e}\n")

        time.sleep(1800)

if __name__ == "__main__":
    run_precision_ict_scanner()