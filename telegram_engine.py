import os
import requests
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.dates as mdates
from dotenv import load_dotenv
from logger import log_ict_trade

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message, image_path=None):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing in .env")
        return
    
    # Send text message
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending text alert: {e}")

    # Send photo with FVG and SL marked
    if image_path and os.path.exists(image_path):
        photo_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        try:
            with open(image_path, "rb") as photo:
                requests.post(photo_url, data={"chat_id": CHAT_ID}, files={"photo": photo})
        except Exception as e:
            print(f"Error sending photo alert: {e}")

def generate_ict_chart(df, setup_info):
    plot_df = df.tail(30).copy()
    if isinstance(plot_df.columns, pd.MultiIndex):
        plot_df.columns = plot_df.columns.get_level_values(0)

    # Line markers for SL, Entry, and TP
    hlines = [setup_info["sl"], setup_info["price"], setup_info["tp"]]
    colors = ['red', 'blue', 'green']

    fig, axlist = mpf.plot(
        plot_df,
        type='candle',
        style='charles',
        title=f"XAUUSD 15M - {setup_info['type']} Setup",
        ylabel='Price ($)',
        hlines=dict(hlines=hlines, colors=colors, linestyle='--'),
        returnfig=True,
        figsize=(10, 6)
    )

    ax = axlist[0]
    
    # Highlight the FVG box region on the chart
    fvg_top = setup_info["fvg_top"]
    fvg_bottom = setup_info["fvg_bottom"]
    ax.axhspan(fvg_bottom, fvg_top, color='gold', alpha=0.3, label='FVG Zone')
    
    # Annotate SL and FVG
    ax.text(plot_df.index[-1], setup_info["sl"], f" SL: ${setup_info['sl']:.2f}", color='red', fontweight='bold')
    ax.text(plot_df.index[-1], (fvg_top + fvg_bottom) / 2, " FVG Zone", color='darkgoldenrod', fontweight='bold')

    chart_file = "ict_setup.png"
    fig.savefig(chart_file, bbox_inches='tight')
    return chart_file

def detect_ict_setup():
    data = yf.download(tickers="GC=F", period="5d", interval="15m", progress=False)
    if data.empty or len(data) < 5:
        return None, None

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
        setup = {
            "type": "BUY",
            "price": current_price,
            "setup": f"15M Bullish FVG ({gap}) + BOS",
            "tp": current_price + 15.0,
            "sl": c1_low,
            "fvg_top": c3_low,
            "fvg_bottom": c1_high
        }
        return setup, data
    elif bearish_fvg:
        gap = f"${c3_high:.2f} - ${c1_low:.2f}"
        setup = {
            "type": "SELL",
            "price": current_price,
            "setup": f"15M Bearish FVG ({gap}) + BOS",
            "tp": current_price - 15.0,
            "sl": c1_high,
            "fvg_top": c1_low,
            "fvg_bottom": c3_high
        }
        return setup, data
    
    return None, None

def run_ict_scanner():
    print("Scanning Gold (XAUUSD) for 15M ICT Setups...")
    setup, data = detect_ict_setup()
    
    if setup:
        s_type = setup["type"]
        s_price = setup["price"]
        s_setup = setup["setup"]
        s_tp = setup["tp"]
        s_sl = setup["sl"]
        
        # Generate chart with FVG box and SL line
        chart_path = generate_ict_chart(data, setup)
        
        alert_msg = (
            "🚀 *PROJECT OMEGA ICT SIGNAL*\n\n"
            f"Asset: Gold (XAUUSD)\n"
            f"Type: {s_type}\n"
            f"Entry: ${s_price:.2f}\n"
            f"Confluence: {s_setup}\n"
            f"TP: ${s_tp:.2f} | SL: ${s_sl:.2f}"
        )
        
        send_telegram_alert(alert_msg, image_path=chart_path)
        log_ict_trade(s_type, s_price, s_setup, s_tp, s_sl)
        print(f"Signal Found: {s_type} logged, plotted, and pushed!")
    else:
        print("Scan complete. No active FVG/BOS setup on current 15M candle.")

if __name__ == "__main__":
    run_ict_scanner()