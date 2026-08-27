import os
import csv
import datetime
import requests
import yfinance as yf
import pandas as pd
import MetaTrader5 as mt5
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LOG_FILE = "trades_log.csv"

# --- Dynamic Risk Management Engine ---
def calculate_dynamic_lot_size(risk_percent, entry_price, sl_price):
    if not mt5.initialize():
        return 0.01  # Safe fallback if MT5 info fetch fails
        
    account_info = mt5.account_info()
    mt5.shutdown()
    
    if account_info is None:
        return 0.01
    
    balance = account_info.balance
    risk_amount = balance * (risk_percent / 100.0)  # 1% of balance
    sl_distance = abs(entry_price - sl_price)       # Stop distance in dollars
    
    if sl_distance == 0:
        return 0.01
        
    # Gold contract formula: 1 Standard Lot = 100 oz ($1 move = $100 per 1.0 lot)
    raw_lot = risk_amount / (sl_distance * 100.0)
    
    # Round to MT5 0.01 minimum lot step
    calculated_lot = round(raw_lot, 2)
    return max(0.01, calculated_lot)

# --- MT5 Execution Engine ---
def execute_mt5_order(symbol, setup_type, price, sl, tp, risk_percent=1.0):
    if not mt5.initialize():
        print(f"❌ MT5 Connection Failed: {mt5.last_error()}")
        return False

    selected_symbol = symbol
    symbol_info = mt5.symbol_info(selected_symbol)
    if symbol_info is None:
        selected_symbol = "GOLD"
        symbol_info = mt5.symbol_info(selected_symbol)
        if symbol_info is None:
            print("❌ Symbol XAUUSDm/GOLD not found in Exness MT5.")
            mt5.shutdown()
            return False

    if not symbol_info.visible:
        mt5.symbol_select(selected_symbol, True)

    # Dynamic Lot Calculation
    lot_size = calculate_dynamic_lot_size(risk_percent, price, sl)
    print(f"🎯 Dynamic Risk Manager: Calculated Lot Size = {lot_size} (Risking {risk_percent}% of balance)")

    order_type = mt5.ORDER_TYPE_BUY_LIMIT if setup_type == "BUY" else mt5.ORDER_TYPE_SELL_LIMIT

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": selected_symbol,
        "volume": float(lot_size),
        "type": order_type,
        "price": float(price),
        "sl": float(sl),
        "tp": float(tp),
        "deviation": 20,
        "magic": 999111,
        "comment": "Project Omega Dynamic Execution",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"✅ Exness Order Placed! Ticket: {result.order}")
        mt5.shutdown()
        return True
    else:
        print(f"❌ MT5 Execution Failed (Error Code: {result.retcode})")
        mt5.shutdown()
        return False

# --- Telegram Alert Dispatcher ---
def send_telegram_alert(message_text, setup_type, current_price, take_profit):
    if setup_type == "SELL" and current_price <= take_profit:
        print("Setup Invalidated: Price hit TP before entry.")
        return
    elif setup_type == "BUY" and current_price >= take_profit:
        print("Setup Invalidated: Price hit TP before entry.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message_text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- Main Engine ---
def run_project_omega():
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n--- Running Project Omega Engine [{timestamp}] ---")

    data_15m = yf.download("GC=F", period="5d", interval="15m", progress=False)
    data_1h = yf.download("GC=F", period="10d", interval="1h", progress=False)

    if data_15m.empty or data_1h.empty:
        return

    if isinstance(data_15m.columns, pd.MultiIndex):
        data_15m.columns = data_15m.columns.get_level_values(0)
    if isinstance(data_1h.columns, pd.MultiIndex):
        data_1h.columns = data_1h.columns.get_level_values(0)

    htf_bias = "BUY" if data_1h['Close'].iloc[-1] > data_1h['Open'].iloc[-1] else "SELL"
    last_close = round(float(data_15m['Close'].iloc[-1]), 2)
    recent_low = round(float(data_15m['Low'].tail(20).min()), 2)
    recent_high = round(float(data_15m['High'].tail(20).max()), 2)

    demand_zone = recent_low + 5.0
    supply_zone = recent_high - 5.0

    if last_close >= supply_zone and htf_bias == "SELL":
        entry, sl, tp = last_close, round(recent_high + 3.0, 2), round(recent_low - 3.0, 2)
        send_telegram_alert(f"🚀 *PROJECT OMEGA SELL SIGNAL*\nEntry: ${entry} | SL: ${sl} | TP: ${tp}", "SELL", entry, tp)
        execute_mt5_order("XAUUSDm", "SELL", entry, sl, tp, risk_percent=1.0)

    elif last_close <= demand_zone and htf_bias == "BUY":
        entry, sl, tp = last_close, round(recent_low - 3.0, 2), round(recent_high + 3.0, 2)
        send_telegram_alert(f"🚀 *PROJECT OMEGA BUY SIGNAL*\nEntry: ${entry} | SL: ${sl} | TP: ${tp}", "BUY", entry, tp)
        execute_mt5_order("XAUUSDm", "BUY", entry, sl, tp, risk_percent=1.0)

    else:
        print(f"Market at ${last_close} | HTF Bias: {htf_bias} | No setup found. Waiting...")

if __name__ == "__main__":
    run_project_omega()