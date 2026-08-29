import json
import os
import subprocess
from datetime import datetime

LOG_FILE = "trade_log.json"

def push_to_github():
    try:
        subprocess.run(["git", "add", LOG_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "auto: update trade_log.json"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("?? Automatically synced trade_log.json to GitHub!")
    except Exception as e:
        print(f"?? Git push failed: {e}")

def log_ict_trade(symbol, trade_type, lot_size, price, sl):
    p_val = float(price) if price is not None else 0.0
    sl_val = float(sl) if sl is not None else 0.0

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": str(symbol),
        "type": str(trade_type),
        "lot_size": float(lot_size),
        "price": f"",
        "sl": f""
    }

    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []

    logs.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

    print("?? Trade successfully logged to trade_log.json")
    push_to_github()
