import os
import requests
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from logger import log_ict_trade

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

def detect_ict_setup():
    data = yf.download(tickers="GC=F", period="5d", interval="15m", progress=False)
    if data.empty or len(data) < 5:
        return None

    c1 = data.iloc[-4]
    c2 = data.iloc[-3]
    c3 = data.iloc[-2]
    
    c1_high = float(c1["High"].iloc[0]) if isinstance(c1["High"], pd.Series) else float(c1["High"])
    c1_low = float(c1["Low"].iloc[0]) if isinstance(c1["Low"], pd.Series) else float(c1["Low"])
    c3_high = float(c3["High"].iloc[0]) if isinstance(c3["High"], pd.Series) else float(c3["High"])
    c3_low = float(c3["Low"].iloc[0]) if isinstance(c3["Low"], pd.Series) else float(c3["Low"])
    
    close_val = data.iloc[-1]["Close"]
    current_price = float(close_val.iloc[0]) if isinstance(close_val, pd.Series) else float(close_val)

    bullish_fvg = c1_high < c3_low
    bearish_fvg = c1_low > c3_high

    if bullish_fvg:
        gap = f"${c1_high:.2f} - ${c3_low:.2f}"
        return {
            "type": "BUY",
            "price": current_price,
            "setup": f"15M Bullish FVG ({gap}) + BOS",
            "tp": current_price + 15.0,
            "sl": c1_low
        }
    elif bearish_fvg:
        gap = f"${c3_high:.2f} - ${c1_low:.2f}"
        return {
            "type": "SELL",
            "price": current_price,
            "setup": f"15M Bearish FVG ({gap}) + BOS",
            "tp": current_price - 15.0,
            "sl": c1_high
        }
    
    return None

def run_ict_scanner():
    print("Scanning Gold (XAUUSD) for 15M ICT Setups...")
    setup = detect_ict_setup()
    
    if setup:
        s_type = setup["type"]
        s_price = setup["price"]
        s_setup = setup["setup"]
        s_tp = setup["tp"]
        s_sl = setup["sl"]
        
        alert_msg = (
            "🚀 *PROJECT OMEGA ICT SIGNAL*\n\n"
            f"Asset: Gold (XAUUSD)\n"
            f"Type: {s_type}\n"
            f"Entry: ${s_price:.2f}\n"
            f"Confluence: {s_setup}\n"
            f"TP: ${s_tp:.2f} | SL: ${s_sl:.2f}"
        )
        
        send_telegram_alert(alert_msg)
        log_ict_trade(s_type, s_price, s_setup, s_tp, s_sl)
        print(f"Signal Found: {s_type} logged and pushed!")
    else:
        print("Scan complete. No active FVG/BOS setup on current 15M candle.")

if __name__ == "__main__":
    run_ict_scanner()