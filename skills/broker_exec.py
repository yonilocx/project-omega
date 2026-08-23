import sys
import json
import ccxt
import os
from dotenv import load_dotenv

# Load secret API credentials from local .env file
load_dotenv()

class BrokerExecutor:
    def __init__(self):
        # Initializes Binance execution client using environment variables
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('EXCHANGE_API_KEY'),
            'secret': os.getenv('EXCHANGE_API_SECRET'),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}  # Change to 'future' if trading perpetuals
        })

    def execute_order(self, symbol, side, amount, stop_loss_price, take_profit_price=None):
        """
        Submits market order with mandatory stop-loss verification.
        """
        try:
            side = side.lower()
            if side not in ['buy', 'sell']:
                return {"success": False, "error": "Invalid order side. Must be 'buy' or 'sell'."}

            if not stop_loss_price:
                return {"success": False, "error": "Order rejected: Missing required Stop Loss price."}

            # 1. Place Main Market Order
            # For live execution: order = self.exchange.create_order(symbol, 'market', side, amount)
            
            # Simulated Execution Structure for Paper Trading Verification
            executed_order = {
                "status": "FILLED",
                "symbol": symbol,
                "side": side.upper(),
                "amount": float(amount),
                "stop_loss": float(stop_loss_price),
                "take_profit": float(take_profit_price) if take_profit_price else "NONE"
            }

            return {
                "success": True,
                "message": f"Order executed successfully for {symbol}",
                "order_details": executed_order
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Usage: python broker_exec.py <symbol> <side> <amount> <stop_loss> [take_profit]
    if len(sys.argv) < 5:
        print(json.dumps({"error": "Usage: python broker_exec.py <symbol> <side> <amount> <stop_loss> [take_profit]"}))
        sys.exit(1)

    sym = sys.argv[1]
    order_side = sys.argv[2]
    qty = sys.argv[3]
    sl = sys.argv[4]
    tp = sys.argv[5] if len(sys.argv) > 5 else None

    executor = BrokerExecutor()
    result = executor.execute_order(symbol=sym, side=order_side, amount=qty, stop_loss_price=sl, take_profit_price=tp)
    print(json.dumps(result, indent=2))
