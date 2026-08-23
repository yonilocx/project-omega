import sys
import json
import os
import ccxt
import pandas as pd
from datetime import datetime

HISTORY_FILE = "trade_history.json"

def detect_smc_levels(df):
    """
    Scans candlestick history for Order Blocks and Fair Value Gaps.
    """
    order_blocks = []
    fvgs = []

    for i in range(2, len(df)):
        c0 = df.iloc[i-2]  # 2 candles back
        c1 = df.iloc[i-1]  # 1 candle back
        c2 = df.iloc[i]    # Current candle

        # 1. Detect Bullish Fair Value Gap
        if c2['low'] > c0['high']:
            fvgs.append({
                "type": "BULLISH_FVG",
                "top": float(c2['low']),
                "bottom": float(c0['high'])
            })
        
        # 2. Detect Bearish Fair Value Gap
        elif c2['high'] < c0['low']:
            fvgs.append({
                "type": "BEARISH_FVG",
                "top": float(c0['low']),
                "bottom": float(c2['high'])
            })

        # 3. Detect Bullish Order Block
        if c1['close'] < c1['open'] and c2['close'] > c2['open'] and (c2['close'] - c2['open']) > (c1['open'] - c1['close']) * 1.5:
            order_blocks.append({
                "type": "BULLISH_OB",
                "high": float(c1['high']),
                "low": float(c1['low'])
            })

        # 4. Detect Bearish Order Block
        elif c1['close'] > c1['open'] and c2['close'] < c2['open'] and (c2['open'] - c2['close']) > (c1['close'] - c1['open']) * 1.5:
            order_blocks.append({
                "type": "BEARISH_OB",
                "high": float(c1['high']),
                "low": float(c1['low'])
            })

    latest_ob = order_blocks[-1] if order_blocks else None
    latest_fvg = fvgs[-1] if fvgs else None

    return latest_ob, latest_fvg

def generate_signal(current_price, ema20, ema50, ob, fvg):
    """
    Generates explicit BUY, SELL, or HOLD decisions based on price action + indicators.
    """
    signal = "HOLD"
    reason = "No high-probability setup detected."

    # BUY SIGNAL CONDITIONS: Bullish EMA trend + price retesting Bullish Order Block or Bullish FVG
    if ema20 > ema50:
        if ob and ob['type'] == "BULLISH_OB" and current_price <= ob['high']:
            signal = "BUY"
            reason = "Bullish trend confirmed. Price retesting Bullish Order Block."
        elif fvg and fvg['type'] == "BULLISH_FVG" and current_price <= fvg['top']:
            signal = "BUY"
            reason = "Bullish trend confirmed. Price filled Bullish Fair Value Gap."

    # SELL SIGNAL CONDITIONS: Bearish EMA trend + price retesting Bearish Order Block or Bearish FVG
    elif ema20 < ema50:
        if ob and ob['type'] == "BEARISH_OB" and current_price >= ob['low']:
            signal = "SELL"
            reason = "Bearish trend confirmed. Price retesting Bearish Order Block."
        elif fvg and fvg['type'] == "BEARISH_FVG" and current_price >= fvg['bottom']:
            signal = "SELL"
            reason = "Bearish trend confirmed. Price filled Bearish Fair Value Gap."

    return signal, reason

def save_to_history(record):
    """
    Saves every scan result and signal to a JSON history file.
    """
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []

    history.append(record)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def fetch_market_data(symbol="BTC/USDT", timeframe="15m", limit=50):
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

        latest = df.iloc[-1]
        current_price = float(latest['close'])
        ema20 = float(latest['ema_20'])
        ema50 = float(latest['ema_50'])

        latest_ob, latest_fvg = detect_smc_levels(df)
        signal, reason = generate_signal(current_price, ema20, ema50, latest_ob, latest_fvg)

        record = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "signal": signal,
            "reason": reason,
            "ema_20": round(ema20, 2),
            "ema_50": round(ema50, 2),
            "order_block": latest_ob,
            "fvg": latest_fvg
        }

        # Save scan to history
        save_to_history(record)

        return record

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asset = sys.argv[1] if len(sys.argv) > 1 else "BTC/USDT"
    tf = sys.argv[2] if len(sys.argv) > 2 else "15m"

    data = fetch_market_data(symbol=asset, timeframe=tf)
    print(json.dumps(data, indent=2))
