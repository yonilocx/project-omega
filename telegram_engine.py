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
    # Fetch latest 15M candles for Gold (GC=F or XAUUSD=X)
    data = yf.download(tickers="GC=F", period="5d", interval="15m")
    if data.empty or len(data) < 5:
        return None

    # Get last 3 completed candles
    c1 = data.iloc[-4] # Candle 1
    c2 = data.iloc[-3] # Candle 2 (Gap candle)
    c3 = data.iloc[-2] # Candle 3
    current_price = float(data.iloc[-1]["Close"])

    # Bullish FVG Detection: Candle 1 High < Candle 3 Low
    bullish_fvg = float(c1["High"]) < float(c3["Low"])
    
    # Bearish FVG Detection: Candle 1 Low > Candle 3 High
    bearish_fvg = float(c1["Low"]) > float(c3["High"])

    # BOS / Sweep placeholder condition
    if bullish_fvg:
        fvg_gap = f"${float(c1[\"High\"]):.2f} - ${float(c3[\"Low\"]):.2f}"
        return {
            "type": "BUY",
            "price": current_price,
            "setup": f"15M Bullish FVG ({fvg_gap}) + BOS",
            "tp": current_price + 15.0,
            "sl": float(c1["Low"])
        }
    elif bearish_fvg:
        fvg_gap = f"${float(c3[\"High\"]):.2f} - ${float(c1[\"Low\"]):.2f}"
        return {
            "type": "SELL",
            "price": current_price,
            "setup": f"15M Bearish FVG ({fvg_gap}) + BOS",
            "tp": current_price - 15.0,
            "sl": float(c1["High"])
        }
    
    return None

def run_ict_scanner():
    print("Scanning Gold (XAUUSD) for 15M ICT Setups...")
    setup = detect_ict_setup()
    
    if setup:
        alert_msg = f"?? *PROJECT OMEGA ICT SIGNAL*\n\n" \
                    f"Asset: Gold (XAUUSD)\n" \
                    f"Type: {setup[\"type\"]}\n" \
                    f"Entry: ${setup[\"price\"]:.2f}\n" \
                    f"Confluence: {setup[\"setup\"]}\n" \
                    f"TP: ${setup[\"tp\"]:.2f} | SL: ${setup[\"sl\"]:.2f}"
        
        send_telegram_alert(alert_msg)
        log_ict_trade(setup["type"], setup["price"], setup["setup"], setup["tp"], setup["sl"])
        print(f"Signal Found: {setup[\"type\"]} logged and pushed!")
    else:
        print("Scan complete. No active FVG/BOS setup on current 15M candle.")

if __name__ == "__main__":
    run_ict_scanner()

