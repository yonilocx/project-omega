from flask import Flask, jsonify, request
from main import evaluate_confidence, SYMBOLS, CONFIDENCE_THRESHOLD
from skills.fetch_data import fetch_market_data

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "active",
        "symbols": SYMBOLS,
        "confidence_threshold": CONFIDENCE_THRESHOLD
    })

@app.route('/scan', methods=['GET'])
def scan():
    results = {}
    for sym in SYMBOLS:
        data = fetch_market_data(sym)
        score, reason = evaluate_confidence(data)
        results[sym] = {
            "price": data.get("current_price"),
            "signal": data.get("signal"),
            "confidence": score,
            "reason": reason
        }
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
