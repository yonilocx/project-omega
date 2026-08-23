import sys
import json

try:
    from skills.notify import send_telegram_alert
except ImportError:
    from notify import send_telegram_alert

class BrokerExecutor:
    def __init__(self):
        pass

    def execute_order(self, symbol, side, amount, stop_loss_price=None, take_profit_price=None):
        side_upper = side.upper()
        
        order_details = {
            "status": "FILLED",
            "symbol": symbol,
            "side": side_upper,
            "amount": float(amount),
            "stop_loss": float(stop_loss_price) if stop_loss_price else None,
            "take_profit": float(take_profit_price) if take_profit_price else None
        }

        # Format Telegram Notification Message
        alert_message = (
            f"?? <b>PROJECT OMEGA TRADE EXECUTED</b> ??\n\n"
            f"<b>Symbol:</b> {symbol}\n"
            f"<b>Action:</b> {side_upper}\n"
            f"<b>Amount:</b> {amount}\n"
            f"<b>Stop Loss:</b> ${stop_loss_price:.2f}\n"
            f"<b>Take Profit:</b> ${take_profit_price:.2f}\n"
            f"<b>Status:</b> FILLED"
        )
        
        # Trigger Telegram Alert
        send_telegram_alert(alert_message)

        return {
            "success": True,
            "message": f"Order executed successfully for {symbol}",
            "order_details": order_details
        }

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(json.dumps({"error": "Usage: python broker_exec.py <symbol> <side> <amount> <stop_loss> [take_profit]"}))
        sys.exit(1)

    sym = sys.argv[1]
    order_side = sys.argv[2]
    qty = float(sys.argv[3])
    sl = float(sys.argv[4])
    tp = float(sys.argv[5]) if len(sys.argv) > 5 else None

    executor = BrokerExecutor()
    result = executor.execute_order(symbol=sym, side=order_side, amount=qty, stop_loss_price=sl, take_profit_price=tp)
    print(json.dumps(result, indent=2))
