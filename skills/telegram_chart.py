# -*- coding: utf-8 -*-
import os
import ccxt
import pandas as pd
import mplfinance as mpf
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def fetch_candle_data(symbol="BTC/USDT", timeframe="15m", limit=60):
    """Fetches real-time candles from Binance."""
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

def generate_and_send_chart(symbol="BTC/USDT", signal_type="BUY", entry=None, sl=None, tp=None):
    """Renders a custom chart PNG and sends it to Telegram."""
    df = fetch_candle_data(symbol)
    
    image_path = "trade_snapshot.png"
    
    # Custom Dark Mode Styling
    mc = mpf.make_marketcolors(
        up='#089981', down='#F23645',
        edge='inherit', wick='inherit', volume='in'
    )
    style = mpf.make_mpf_style(
        base_mpf_style='charles',
        marketcolors=mc,
        gridstyle=':',
        facecolor='#131722',
        figcolor='#131722'
    )
    
    # Configure horizontal lines for Entry, SL, and TP
    hlines_list = []
    colors_list = []
    
    if entry:
        hlines_list.append(entry)
        colors_list.append('#2962FF') # Blue for Entry
    if sl:
        hlines_list.append(sl)
        colors_list.append('#F23645') # Red for Stop Loss
    if tp:
        hlines_list.append(tp)
        colors_list.append('#089981') # Green for Take Profit

    plot_kwargs = {}
    if hlines_list:
        plot_kwargs['hlines'] = dict(
            hlines=hlines_list,
            colors=colors_list,
            linestyle='--',
            linewidths=1.5
        )

    # Render Chart to File
    title_text = f"Project Omega Signal: {signal_type} {symbol}"
    mpf.plot(
        df,
        type='candle',
        style=style,
        title=title_text,
        volume=False,
        savefig=image_path,
        **plot_kwargs
    )

    # Send Image to Telegram Bot
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    caption = f"🚀 **Project Omega Trade Executed**\n\n📌 **Symbol:** {symbol}\n📈 **Action:** {signal_type}"
    if entry: caption += f"\n🎯 **Entry:** ${entry}"
    if sl: caption += f"\n🛑 **Stop Loss:** ${sl}"
    if tp: caption += f"\n✅ **Take Profit:** ${tp}"

    with open(image_path, 'rb') as photo:
        payload = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
        files = {"photo": photo}
        response = requests.post(url, data=payload, files=files)
        
    # Clean up local image
    if os.path.exists(image_path):
        os.remove(image_path)
        
    if response.status_code == 200:
        print("Chart image successfully sent to Telegram!")
    else:
        print(f"Failed to send image: {response.text}")

if __name__ == "__main__":
    print("Generating and sending test chart to Telegram...")
    generate_and_send_chart("BTC/USDT", "BUY", entry=96000, sl=95500, tp=97500)
