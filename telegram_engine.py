def calculate_lot_size(account_balance=100.0, risk_pct=0.02, entry_price=0.0, stop_loss_price=0.0, lot_step=0.01):
    """
    Calculates exact lot size for moderate risk management ($2.00 risk on $100 balance).
    """
    max_risk_dollars = account_balance * risk_pct  # $2.00
    sl_distance = abs(entry_price - stop_loss_price)
    
    if sl_distance == 0:
        return 0.01

    # Standard CFD calculation: 1.0 lot on XAU/USD = $100 per $1 move
    # 0.01 lot = $1.00 per $1 move
    raw_lot = max_risk_dollars / (sl_distance * 100)
    
    # Round down to the nearest allowed lot step
    lot_size = max(lot_step, round(raw_lot / lot_step) * lot_step)
    return round(lot_size, 3)