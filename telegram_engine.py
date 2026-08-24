def calculate_lot_size(account_balance=100.0, risk_pct=0.02, entry_price=0.0, stop_loss_price=0.0, min_lot=0.01):
    """
    Calculates exact lot size for moderate risk management ($2.00 risk on $100 balance).
    Gold (XAU/USD): 0.01 lot = $1.00 risk per $1.00 price movement.
    """
    max_risk_dollars = account_balance * risk_pct  # $2.00 max loss
    sl_distance = abs(entry_price - stop_loss_price)  # E.g., $4,700 - $4,692 = $8.00 SL distance
    
    if sl_distance == 0:
        return min_lot

    # Standard CFD math: 0.01 lot risks $1 per $1.00 move in Gold
    raw_lot = max_risk_dollars / sl_distance
    
    # Cap to broker minimum (0.01 micro lot)
    final_lot = max(min_lot, round(raw_lot, 2))
    return final_lot