import MetaTrader5 as mt5
from datetime import datetime, timezone

def get_active_symbol():
    """Returns XAUUSDm on weekdays and BTCUSDm on weekends."""
    now = datetime.now(timezone.utc)
    # Weekend window: Friday after 21:00 UTC through Sunday before 22:00 UTC
    if now.weekday() == 5:  # Saturday
        return "BTCUSDm"
    if now.weekday() == 6 and now.hour < 22:  # Sunday before Gold opens
        return "BTCUSDm"
    if now.weekday() == 4 and now.hour >= 21:  # Friday after Gold closes
        return "BTCUSDm"
    
    return "XAUUSDm"

def print_monday_report():
    """Generates trade performance report for XAUUSDm and BTCUSDm."""
    now = datetime.now(timezone.utc)
    # Check if today is Monday morning (e.g. 00:00 - 01:00 UTC window)
    if now.weekday() == 0 and now.hour == 0:
        if not mt5.initialize():
            return
            
        # Get historical deals from past 7 days
        from_time = datetime(now.year, now.month, now.day - 7, tzinfo=timezone.utc)
        history = mt5.history_deals_get(from_time, now)
        
        if history:
            gold_profit = sum(d.profit for d in history if d.symbol == "XAUUSDm")
            btc_profit = sum(d.profit for d in history if d.symbol == "BTCUSDm")
            
            print("\n========================================")
            print("       PROJECT OMEGA WEEKLY REPORT       ")
            print("========================================")
            print(f"  Gold (XAUUSDm) Profit: ${gold_profit:.2f}")
            print(f"  Bitcoin (BTCUSDm) Profit: ${btc_profit:.2f}")
            print(f"  Total Profit: ${gold_profit + btc_profit:.2f}")
            print("========================================\n")

def execute_trade(target_profit_usd=2.00, stop_loss_usd=3.00, risk_percent=0.01):
    print_monday_report()

    symbol = get_active_symbol()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Active Symbol: {symbol}")

    if not mt5.initialize():
        print("MT5 Initialization failed")
        return

    # Skip execution cycle if a trade is already open on this symbol
    positions = mt5.positions_get(symbol=symbol)
    if positions and len(positions) > 0:
        print(f"Position already active for {symbol}. Skipping cycle.")
        return

    # Retrieve account balance & latest prices
    account_info = mt5.account_info()
    tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)

    if not account_info or not tick or not symbol_info:
        print(f"Failed to pull market/account data for {symbol}")
        return

    balance = account_info.balance

    # Calculate lot size dynamically
    lot = max(symbol_info.volume_min, round((balance * risk_percent) / 100, 2))

    # Order Direction (Default: BUY)
    order_type = mt5.ORDER_TYPE_BUY
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    # Calculate TP / SL distances
    # Symbol contract size: Gold = 100, BTC = 1
    contract_size = symbol_info.trade_contract_size if symbol_info.trade_contract_size > 0 else 1
    tp_distance = target_profit_usd / (lot * contract_size)
    sl_distance = stop_loss_usd / (lot * contract_size)

    tp_price = price + tp_distance if order_type == mt5.ORDER_TYPE_BUY else price - tp_distance
    sl_price = price - sl_distance if order_type == mt5.ORDER_TYPE_BUY else price + sl_distance

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 20,
        "magic": 123456,
        "comment": f"Omega $2 Target ({symbol})",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed for {symbol}: {result.comment}")
    else:
        print(f"Trade executed! Symbol: {symbol} | Ticket: {result.order}")

if __name__ == "__main__":
    execute_trade()