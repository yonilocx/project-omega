import ccxt
import pandas as pd

def fetch_market_data(symbol="BTC/USDT", timeframe="15m", limit=100):
    try:
        exchange = ccxt.binanceusdm({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        # Map XAU/USDT directly to Binance USD-M ticker
        target_symbol = "XAUUSDT" if symbol in ["XAU/USDT", "XAUUSD", "XAU/USDT:USDT"] else symbol.replace("/", "")
        
        ohlcv = exchange.fetch_ohlcv(target_symbol, timeframe=timeframe, limit=limit)
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        
        current_price = float(df['close'].iloc[-1])
        ema_20 = float(df['ema_20'].iloc[-1])
        ema_50 = float(df['ema_50'].iloc[-1])

        signal = "HOLD"
        reason = "Ranging / No clear ICT confluence"
        
        if current_price > ema_20 > ema_50:
            signal = "BUY"
            reason = "Bullish structure & EMA alignment"
        elif current_price < ema_20 < ema_50:
            signal = "SELL"
            reason = "Bearish structure & EMA alignment"

        order_block = {
            "type": "BULLISH_OB" if signal == "BUY" else "BEARISH_OB",
            "high": float(df['high'].iloc[-3]),
            "low": float(df['low'].iloc[-3])
        }
        
        fvg = {
            "top": float(df['high'].iloc[-2]),
            "bottom": float(df['low'].iloc[-2])
        }

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "signal": signal,
            "reason": reason,
            "ema_20": ema_20,
            "ema_50": ema_50,
            "order_block": order_block,
            "fvg": fvg
        }
    except Exception as e:
        print(f"Fetch error for {symbol}: {e}")
        return {"symbol": symbol, "current_price": 0.0, "signal": "HOLD"}

if __name__ == "__main__":
    import json
    print(json.dumps(fetch_market_data("XAU/USDT"), indent=2))
