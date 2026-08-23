# -*- coding: utf-8 -*-
import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
secret_key = os.getenv("BINANCE_SECRET_KEY")

# Initialize Binance USDT-M Futures
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'  # Futures execution mode
    }
})

def check_futures_balance(asset="USDT"):
    try:
        balance = exchange.fetch_balance()
        return balance['free'].get(asset, 0.0)
    except Exception as e:
        print(f"Error fetching futures balance: {e}")
        return None

def set_leverage(symbol, leverage=10):
    try:
        response = exchange.set_leverage(leverage, symbol)
        print(f"Leverage set to {leverage}x for {symbol}")
        return response
    except Exception as e:
        print(f"Failed to set leverage for {symbol}: {e}")
        return None

def execute_futures_order(symbol, side, amount, stop_loss=None, take_profit=None):
    """Executes market order on Binance USDT-M Futures with optional SL/TP."""
    try:
        side = side.lower()
        print(f"Sending Futures {side.upper()} order for {symbol} | Amount: {amount}")
        
        # Primary Entry Order
        order = exchange.create_market_order(symbol, side, amount)
        print(f"Entry Executed! Order ID: {order['id']}")

        # Opposite side for exits
        exit_side = 'sell' if side == 'buy' else 'buy'

        # Stop Loss
        if stop_loss:
            exchange.create_order(
                symbol=symbol,
                type='STOP_MARKET',
                side=exit_side,
                amount=amount,
                params={'stopPrice': stop_loss, 'reduceOnly': True}
            )
            print(f"Stop Loss set at {stop_loss}")

        # Take Profit
        if take_profit:
            exchange.create_order(
                symbol=symbol,
                type='TAKE_PROFIT_MARKET',
                side=exit_side,
                amount=amount,
                params={'stopPrice': take_profit, 'reduceOnly': True}
            )
            print(f"Take Profit set at {take_profit}")

        return order
    except Exception as e:
        print(f"Futures Execution Failed: {e}")
        return None

if __name__ == "__main__":
    print("Testing Binance USDT-M Futures Connection...")
    usdt_bal = check_futures_balance("USDT")
    if usdt_bal is not None:
        print(f"Futures Balance: ${usdt_bal} USDT")
    else:
        print("Failed to connect to Futures API. Make sure 'Enable Futures' is checked in your Binance API settings.")
