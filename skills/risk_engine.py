import sys
import json

class RiskEngine:
    def __init__(self, max_daily_drawdown=30.0, max_risk_per_trade=0.02):
        self.max_daily_drawdown = max_daily_drawdown
        self.max_risk_per_trade = max_risk_per_trade

    def evaluate(self, balance, entry, stop_loss, daily_loss=0.0):
        balance = float(balance)
        entry = float(entry)
        stop_loss = float(stop_loss)
        daily_loss = float(daily_loss)

        if daily_loss >= self.max_daily_drawdown:
            return {
                "approved": False,
                "reason": f"Daily drawdown limit reached (${daily_loss:.2f} >= ${self.max_daily_drawdown:.2f}). No new trades allowed.",
                "position_size": 0
            }

        risk_amount = balance * self.max_risk_per_trade
        price_risk = abs(entry - stop_loss)

        if price_risk == 0:
            return {
                "approved": False,
                "reason": "Stop loss price cannot be equal to entry price.",
                "position_size": 0
            }

        position_size = round(risk_amount / price_risk, 4)

        return {
            "approved": True,
            "reason": "Risk checks passed.",
            "risk_amount": risk_amount,
            "position_size": position_size
        }

def calculate_risk(balance=1000, entry=100, stop_loss=98, daily_loss=0):
    engine = RiskEngine()
    return engine.evaluate(balance, entry, stop_loss, daily_loss)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(json.dumps({"error": "Usage: python risk_engine.py <balance> <entry> <stop_loss> [daily_loss]"}))
        sys.exit(1)

    bal = sys.argv[1]
    ent = sys.argv[2]
    sl = sys.argv[3]
    dl = sys.argv[4] if len(sys.argv) > 4 else 0.0

    res = calculate_risk(bal, ent, sl, dl)
    print(json.dumps(res, indent=2))
