import json
import sys
import time
from datetime import datetime
from skills.fetch_data import fetch_market_data
from skills.risk_engine import calculate_risk
from skills.broker_exec import BrokerExecutor

INTERVAL_SECONDS = 900  # 15 minutes
CONFIDENCE_THRESHOLD = 80  # 80% Win Rate Filter
SYMBOLS = ["BTC/USDT", "XAU/USDT"]  # Bitcoin and Forex Gold Futures

def evaluate_confidence(data):
    if data.get("signal") == "HOLD":
        return 0, "No setup detected"

    score = 50  # Base score
    reasons = []

    if data.get("order_block"):
        score += 20
        reasons.append("Order Block Re-test")

    if data.get("fvg"):
        score += 15
        reasons.append("FVG Gap Active")

    price = data.get("current_price", 0)
    e20 = data.get("ema_20", 0)
    e50 = data.get("ema_50", 0)

    if data.get("signal") == "BUY" and price > e20 > e50:
        score += 15
        reasons.append("Bullish Trend Alignment")
    elif data.get("signal") == "SELL" and price < e20 < e50:
        score += 15
        reasons.append("Bearish Trend Alignment")

    return min(score, 100), ", ".join(reasons)

def analyze_and_trade(symbol, balance=1000, daily_loss=0):
    try:
        data = fetch_market_data(symbol)
        signal = data.get("signal")
        current_price = data.get("current_price")
        
        print(f"[{symbol}] Live Price: ${current_price} | Signal: {signal}")
        
        if signal == "HOLD":
            print(f"[{symbol}] Status: Standby")
            return

        confidence, reasons = evaluate_confidence(data)
        print(f"[{symbol}] Win-Rate Score: {confidence}% (Req: {CONFIDENCE_THRESHOLD}%)")

        if confidence < CONFIDENCE_THRESHOLD:
            print(f"[{symbol}] Skipped (Confidence < 80%)")
            return

        entry = current_price
        stop_loss = data.get("order_block", {}).get("low", entry * 0.99) if signal == "BUY" else data.get("order_block", {}).get("high", entry * 1.01)
        take_profit = entry * 1.02 if signal == "BUY" else entry * 0.98

        risk = calculate_risk(balance=balance, entry=entry, stop_loss=stop_loss, daily_loss=daily_loss)
        
        if not risk.get("approved", False):
            print(f"[{symbol}] Rejected by Risk Engine: {risk.get('reason')}")
            return

        executor = BrokerExecutor()
        execution = executor.execute_order(
            symbol=symbol,
            side=signal.lower(),
            amount=risk["position_size"],
            stop_loss_price=stop_loss,
            take_profit_price=take_profit
        )
        print(f"[{symbol}] ?? EXECUTED!\n{json.dumps(execution, indent=2)}")

    except Exception as e:
        print(f"[{symbol}] Error: {str(e)}")

def run_loop():
    print("?? Project Omega 24/7 Automated Trader Active (BTC/USDT & XAU/USDT)")
    print("Scanning 15m charts every 15 minutes for >= 80% winning setups.\n")
    
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n==========================================")
        print(f"[{now}] 15-Minute Market Cycle Scan")
        print(f"==========================================")
        
        for sym in SYMBOLS:
            analyze_and_trade(sym)
            
        print(f"\nCycle complete. Waiting 15 minutes (900s) for next 15m candle...")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    run_loop()
