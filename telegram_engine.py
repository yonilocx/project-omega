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
    """Dispatches 80%+ conviction ICT Gold signal to Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    message = (
        "👑 *PROJECT OMEGA — HIGH-CONVICTION XAU/USD SIGNAL* 👑\n\n"
        f"• *Asset:* Gold (XAU/USD)\n"
        f"• *Session:* {session_name}\n"
        f"• *Bias:* {bias}\n"
        f"• *ICT Confluence:* {setup_detail}\n\n"
        f"🎯 *Optimal Entry (FVG):* ${entry_zone}\n"
        f"🛑 *Invalidation (SL):* ${stop_loss}\n"
        f"✅ *Liquidity Target 1:* ${tp1}\n"
        f"🚀 *Expansion Target 2:* ${tp2}\n\n"
        "⚠️ *Risk Rule:* Set SL to Breakeven upon reaching TP1. Max 1% risk."
    )
    
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def fetch_gold_data():
    """Fetches 15m intraday and 1h trend data for Gold."""
    gold = yf.Ticker("GC=F")
    df_15m = gold.history(period="3d", interval="15m")
    df_1h = gold.history(period="7d", interval="1h")
    return df_15m, df_1h

def check_htf_bias(df_1h):
    """Determines 1H Market Trend (SMA / Structure)."""
    df_1h['SMA20'] = df_1h['Close'].rolling(20).mean()
    last_close = df_1h['Close'].iloc[-1]
    last_sma = df_1h['SMA20'].iloc[-1]
    
    if last_close > last_sma:
        return "BULLISH"
    elif last_close < last_sma:
        return "BEARISH"
    return "NEUTRAL"

def run_precision_ict_scanner():
    now_utc = datetime.now(timezone.utc)
    current_hour = now_utc.hour

    print(f"\n[{now_utc.strftime('%Y-%m-%d %H:%M UTC')}] Analyzing Gold Market Mechanics...")

    try:
        df_15m, df_1h = fetch_gold_data()
        if df_15m.empty or df_1h.empty:
            print("Data feed offline. Retrying next cycle.")
            return

        current_price = round(df_15m['Close'].iloc[-1], 2)
        htf_bias = check_htf_bias(df_1h)

        # Calculate Asian Session Range (00:00 - 06:00 UTC)
        today_str = now_utc.strftime('%Y-%m-%d')
        today_data = df_15m[df_15m.index.strftime('%Y-%m-%d') == today_str]
        tokyo_data = today_data.between_time('00:00', '06:00')

        if tokyo_data.empty:
            print("Asian session liquidity range incomplete.")
            return

        asia_high = round(tokyo_data['High'].max(), 2)
        asia_low = round(tokyo_data['Low'].min(), 2)

        print(f"Price: ${current_price} | Asia High: ${asia_high} | Asia Low: ${asia_low} | HTF Bias: {htf_bias}")

        # Killzone Validations
        is_london = 7 <= current_hour < 10
        is_ny = 12 <= current_hour < 15
        
        if not (is_london or is_ny):
            print(f"[{now_utc.strftime('%H:%M UTC')}] Outside Killzone. Resting to prevent low-volume noise.")
            return

        session_label = "London Killzone" if is_london else "New York Killzone"

        # Confluence Check 1: Bullish Sweep + HTF Confluence
        if current_price < (asia_low - 1.50) and htf_bias in ["BULLISH", "NEUTRAL"]:
            # Verify displacement (15m candle size)
            last_candle_size = abs(df_15m['Close'].iloc[-1] - df_15m['Open'].iloc[-1])
            if last_candle_size >= 2.5:  # Minimum $2.50 displacement for valid FVG
                entry_min = round(asia_low, 2)
                entry_max = round(asia_low + 2.5, 2)
                sl = round(asia_low - 8.0, 2)
                tp1 = round(asia_high, 2)
                tp2 = round(asia_high + 12.0, 2)

                send_gold_signal(
                    bias="Bullish 🟢",
                    entry_zone=f"{entry_min} - {entry_max}",
                    stop_loss=f"{sl}",
                    tp1=f"{tp1}",
                    tp2=f"{tp2}",
                    session_name=session_label,
                    setup_detail=f"Asia Low Sweep (${asia_low}) + HTF Trend Alignment + $2.5+ Displacement FVG"
                )
                print("High-Probability Bullish Signal Dispatched!")

        # Confluence Check 2: Bearish Sweep + HTF Confluence
        elif current_price > (asia_high + 1.50) and htf_bias in ["BEARISH", "NEUTRAL"]:
            last_candle_size = abs(df_15m['Close'].iloc[-1] - df_15m['Open'].iloc[-1])
            if last_candle_size >= 2.5:
                entry_min = round(asia_high - 2.5, 2)
                entry_max = round(asia_high, 2)
                sl = round(asia_high + 8.0, 2)
                tp1 = round(asia_low, 2)
                tp2 = round(asia_low - 12.0, 2)

                send_gold_signal(
                    bias="Bearish 🔴",
                    entry_zone=f"{entry_min} - {entry_max}",
                    stop_loss=f"{sl}",
                    tp1=f"{tp1}",
                    tp2=f"{tp2}",
                    session_name=session_label,
                    setup_detail=f"Asia High Sweep (${asia_high}) + HTF Trend Alignment + $2.5+ Displacement FVG"
                )
                print("High-Probability Bearish Signal Dispatched!")
        else:
            print("No setup meets all 4 high-conviction ICT rules. No signal sent.")

    except Exception as e:
        print(f"Analysis error: {e}")

if __name__ == "__main__":
    print("Project Omega — Precision ICT Gold Loop Running...")
    while True:
        run_precision_ict_scanner()
        time.sleep(1800)  # Runs every 30 minutes