import ccxt
import pandas as pd
from lightweight_charts import Chart

def launch_live_chart(symbol="BTC/USDT", timeframe="5m"):
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    chart = Chart(inner_width=1200, inner_height=700)
    chart.layout(background_color='#0e1117', text_color='#FFFFFF')
    chart.candle_style(up_color='#089981', down_color='#F23645')
    
    chart.set(df)
    
    # Example Trade Marker where AI triggers an order
    chart.marker(text="Project Omega LONG", position="below", color="#089981", shape="arrow_up")
    
    chart.show(block=True)

if __name__ == "__main__":
    launch_live_chart("BTC/USDT")
