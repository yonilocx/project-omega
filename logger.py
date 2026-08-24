import json
import os
from datetime import datetime

LOG_FILE = "trades.json"

def log_ict_trade(signal_type, price, setup_type, tp, sl):
    trade_data = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "type": signal_type,
        "price": f"${price:.2f}",
        "setup": setup_type,
        "tp_sl": f"TP: ${tp:.2f} | SL: ${sl:.2f}"
    }

    trades = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                trades = json.load(f)
            except:
                trades = []

    trades.insert(0, trade_data)

    with open(LOG_FILE, "w") as f:
        json.dump(trades[:20], f, indent=4)

    os.system("git add trades.json index.html")
    os.system('git commit -m "Auto-update ICT Trade Dashboard"')
    os.system("git push origin main")

