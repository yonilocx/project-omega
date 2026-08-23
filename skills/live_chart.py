# -*- coding: utf-8 -*-
import asyncio
import ccxt
import pandas as pd
from lightweight_charts import Chart

async def main():
    exchange = ccxt.binance()
    symbol = "BTC/USDT"
    timeframe = "1m"

    chart = Chart(inner_width=1200, inner_height=700)
    chart.layout(background_color='#131722', text_color='#FFFFFF')
    chart.candle_style(up_color='#089981', down_color='#F23645')

    print(f"Fetching market data for {symbol}...")
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    chart.set(df)

    latest_time = df.iloc[-1]['time']
    chart.marker(
        time=latest_time,
        position='below',
        color='#089981',
        shape='arrow_up',
        text='Project Omega BUY'
    )

    # Open window asynchronously
    await asyncio.gather(
        chart.show_async(),
        stream_updates(exchange, chart, symbol, timeframe)
    )

async def stream_updates(exchange, chart, symbol, timeframe):
    while True:
        await asyncio.sleep(2)
        try:
            updated_bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=2)
            new_df = pd.DataFrame(updated_bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            new_df['time'] = pd.to_datetime(new_df['time'], unit='ms')
            chart.update(new_df.iloc[-1])
        except Exception as e:
            print(f"Update error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
