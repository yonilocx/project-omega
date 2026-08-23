import sys
import json

class RiskEngine:
    def __init__(self, account_balance, max_risk_pct=1.0, max_daily_drawdown_pct=3.0):
        self.account_balance = float(account_balance)
        self.max_risk_pct = float(max_risk_pct)
        self.max_daily_drawdown_pct = float(max_daily_drawdown_pct)

    def calculate_position(self, entry_price, stop_loss_price, daily_realized_loss=0.0):
        entry_price = float(entry_price)
        stop_loss_price = float(stop_loss_price)
        daily_realized_loss = float(daily_realized_loss)

        # 1. Daily Drawdown Guardrail
        max_allowed_daily_loss = self.account_balance * (self.max_daily_drawdown_pct / 100.0)
        if daily_realized_loss >= max_allowed_daily_loss:
            return {
                "approved": False,
                "reason": f"Daily drawdown limit reached (${daily_realized_loss:.2f} >= ${max_allowed_daily_loss:.2f}). No new trades allowed."
            }

        # 2. Stop Loss Distance Check
        price_risk_per_unit = abs(entry_price - stop_loss_price)
        if price_risk_per_unit == 0:
            return {
                "approved": False,
                "reason": "Invalid Stop Loss. Entry price and Stop Loss price cannot be identical."
            }

        # 3. Position Sizing Calculation
        max_dollar_risk = self.account_balance * (self.max_risk_pct / 100.0)
        position_units = max_dollar_risk / price_risk_per_unit

        return {
            "approved": True,
            "account_balance": self.account_balance,
            "max_dollar_risk": round(max_dollar_risk, 2),
            "entry_price": entry_price,
            "stop_loss_price": stop_loss_price,
            "price_risk_per_unit": round(price_risk_per_unit, 4),
            "position_units": round(position_units, 4)
        }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: python risk_engine.py <balance> <entry> <stop_loss> [daily_loss]"}))
        sys.exit(1)

    acc_balance = sys.argv[1]
    entry = sys.argv[2]
    sl = sys.argv[3]
    daily_loss = sys.argv[4] if len(sys.argv) > 4 else 0.0

    engine = RiskEngine(account_balance=acc_balance)
    result = engine.calculate_position(entry_price=entry, stop_loss_price=sl, daily_realized_loss=daily_loss)
    print(json.dumps(result, indent=2))
