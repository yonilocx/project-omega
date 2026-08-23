from flask import Flask, render_template_string
import webbrowser

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Project Omega - Trade History & ICT Visualizer</title>
    <script src="https://unpkg.com/lightweight-charts@4.2.1/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        body { margin: 0; padding: 0; background-color: #0e1117; display: flex; height: 100vh; width: 100vw; overflow: hidden; font-family: sans-serif; }
        .chart-container { width: 50vw; height: 100vh; position: relative; border-right: 1px solid #1f2937; }
        .chart-container:last-child { border-right: none; }
        .chart-header { position: absolute; top: 10px; left: 15px; z-index: 10; color: #FFFFFF; font-size: 13px; font-weight: bold; background: rgba(19, 23, 34, 0.9); padding: 6px 10px; border-radius: 6px; display: flex; align-items: center; gap: 8px; border: 1px solid #2a2e39; }
        .tf-btn { background: #2a2e39; color: #d9d9d9; border: none; padding: 3px 6px; border-radius: 4px; cursor: pointer; font-size: 11px; }
        .tf-btn:hover, .tf-btn.active { background: #2962FF; color: #FFFFFF; }
        .chart-box { width: 100%; height: 100%; position: relative; }
        .ict-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }
    </style>
</head>
<body>
    <div class="chart-container">
        <div class="chart-header">
            <span>BTC/USDT</span>
            <div id="tf-btc">
                <button class="tf-btn active" onclick="changeTF('BTC', '1m', this)">1m</button>
                <button class="tf-btn" onclick="changeTF('BTC', '5m', this)">5m</button>
                <button class="tf-btn" onclick="changeTF('BTC', '15m', this)">15m</button>
                <button class="tf-btn" onclick="changeTF('BTC', '1h', this)">1h</button>
                <button class="tf-btn" onclick="changeTF('BTC', '4h', this)">4h</button>
            </div>
        </div>
        <div id="chart-btc" class="chart-box">
            <canvas id="canvas-btc" class="ict-canvas"></canvas>
        </div>
    </div>
    
    <div class="chart-container">
        <div class="chart-header">
            <span>XAU/USDT</span>
            <div id="tf-xau">
                <button class="tf-btn active" onclick="changeTF('XAU', '1m', this)">1m</button>
                <button class="tf-btn" onclick="changeTF('XAU', '5m', this)">5m</button>
                <button class="tf-btn" onclick="changeTF('XAU', '15m', this)">15m</button>
                <button class="tf-btn" onclick="changeTF('XAU', '1h', this)">1h</button>
                <button class="tf-btn" onclick="changeTF('XAU', '4h', this)">4h</button>
            </div>
        </div>
        <div id="chart-xau" class="chart-box">
            <canvas id="canvas-xau" class="ict-canvas"></canvas>
        </div>
    </div>

    <script>
        const chartOptions = {
            layout: { backgroundColor: '#0e1117', textColor: '#D9D9D9' },
            grid: { vertLines: { color: 'rgba(42, 46, 57, 0.2)' }, horzLines: { color: 'rgba(42, 46, 57, 0.2)' } },
            crosshair: { mode: 0 },
            timeScale: { timeVisible: true, secondsVisible: false, rightOffset: 8 },
            handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: true },
            handleScale: { axisPressedMouseMove: true, mouseWheel: true, pinch: true }
        };

        const chartBTC = LightweightCharts.createChart(document.getElementById('chart-btc'), chartOptions);
        const chartXAU = LightweightCharts.createChart(document.getElementById('chart-xau'), chartOptions);

        const seriesBTC = chartBTC.addCandlestickSeries({ upColor: '#089981', downColor: '#F23645' });
        const seriesXAU = chartXAU.addCandlestickSeries({ upColor: '#089981', downColor: '#F23645' });

        const emaBTC = chartBTC.addLineSeries({ color: '#2962FF', lineWidth: 2 });
        const emaXAU = chartXAU.addLineSeries({ color: '#2962FF', lineWidth: 2 });

        let currentTF_BTC = '1m';
        let currentTF_XAU = '1m';
        let isFirstLoad_BTC = true;
        let isFirstLoad_XAU = true;

        let activeLines_BTC = [];
        let activeLines_XAU = [];
        let state_BTC = {};
        let state_XAU = {};

        function clearLines(series, linesList) {
            linesList.forEach(line => series.removePriceLine(line));
            linesList.length = 0;
        }

        function calculateEMA(data, period) {
            const k = 2 / (period + 1);
            let emaData = [];
            let ema = data[0].close;
            for (let i = 0; i < data.length; i++) {
                ema = data[i].close * k + ema * (1 - k);
                emaData.push({ time: data[i].time, value: ema });
            }
            return emaData;
        }

        function drawTradingViewMarkup(chart, series, canvasId, state) {
            if (!state || !state.cdata) return;
            const canvas = document.getElementById(canvasId);
            const ctx = canvas.getContext('2d');
            const container = canvas.parentElement;
            
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const timeScale = chart.timeScale();

            // 1. Draw Historical Position Blocks (Risk/Reward shaded boxes for past trades)
            if (state.tradeHistory) {
                state.tradeHistory.forEach(trade => {
                    const xStart = timeScale.timeToCoordinate(trade.startTime);
                    const xEnd = timeScale.timeToCoordinate(trade.endTime) || canvas.width - 50;

                    const yEntry = series.priceToCoordinate(trade.entryPrice);
                    const yTP = series.priceToCoordinate(trade.tpPrice);
                    const ySL = series.priceToCoordinate(trade.slPrice);

                    if (xStart && yEntry && yTP && ySL) {
                        const boxWidth = Math.max(xEnd - xStart, 30);

                        // Take Profit Zone
                        ctx.fillStyle = 'rgba(8, 153, 129, 0.2)';
                        ctx.fillRect(xStart, yTP, boxWidth, yEntry - yTP);
                        ctx.strokeStyle = 'rgba(8, 153, 129, 0.6)';
                        ctx.strokeRect(xStart, yTP, boxWidth, yEntry - yTP);

                        // Stop Loss Zone
                        ctx.fillStyle = 'rgba(242, 54, 69, 0.2)';
                        ctx.fillRect(xStart, yEntry, boxWidth, ySL - yEntry);
                        ctx.strokeStyle = 'rgba(242, 54, 69, 0.6)';
                        ctx.strokeRect(xStart, yEntry, boxWidth, ySL - yEntry);
                    }
                });
            }

            // 2. Draw FVG Box
            if (state.fvg) {
                const fvg = state.fvg;
                const xFvgStart = timeScale.timeToCoordinate(fvg.startTime);
                const yFvgTop = series.priceToCoordinate(fvg.top);
                const yFvgBottom = series.priceToCoordinate(fvg.bottom);

                if (xFvgStart && yFvgTop && yFvgBottom) {
                    const fvgWidth = 80;
                    const fvgHeight = Math.abs(yFvgBottom - yFvgTop);
                    const topY = Math.min(yFvgTop, yFvgBottom);

                    ctx.fillStyle = 'rgba(0, 188, 212, 0.25)';
                    ctx.fillRect(xFvgStart, topY, fvgWidth, fvgHeight);
                    ctx.strokeStyle = '#00BCD4';
                    ctx.strokeRect(xFvgStart, topY, fvgWidth, fvgHeight);

                    ctx.fillStyle = '#00BCD4';
                    ctx.font = 'bold 12px sans-serif';
                    ctx.fillText('FVG', xFvgStart + 10, topY + (fvgHeight / 2) + 4);
                }
            }
        }

        function applyICTStrategy(chart, series, emaSeries, cdata, activeLines, canvasId, stateObj) {
            clearLines(series, activeLines);

            const len = cdata.length;
            const resPrice = Math.max(...cdata.slice(len - 50, len - 20).map(d => d.high));
            const supPrice = Math.min(...cdata.slice(len - 50, len - 20).map(d => d.low));

            emaSeries.setData(calculateEMA(cdata, 20));

            // Support & Resistance Lines
            activeLines.push(series.createPriceLine({
                price: resPrice, color: '#F23645', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: true, title: 'Resistance'
            }));
            activeLines.push(series.createPriceLine({
                price: supPrice, color: '#2962FF', lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dashed, axisLabelVisible: true, title: 'Support'
            }));

            // Complete Trade Execution History Markers
            const pastTrade1_Entry = cdata[len - 70];
            const pastTrade1_Exit = cdata[len - 50];
            const pastTrade2_Entry = cdata[len - 40];
            const pastTrade2_Exit = cdata[len - 20];
            const currentTrade_Entry = cdata[len - 15];

            const markers = [
                // Structure Labels
                { time: cdata[len - 80].time, position: 'aboveBar', color: '#888888', shape: 'none', text: 'HH' },
                { time: cdata[len - 60].time, position: 'belowBar', color: '#888888', shape: 'none', text: 'HL' },
                { time: cdata[len - 30].time, position: 'aboveBar', color: '#2962FF', shape: 'none', text: 'BOS' },

                // Historical Trade 1 (WIN)
                { time: pastTrade1_Entry.time, position: 'belowBar', color: '#089981', shape: 'arrowUp', text: 'BUY @ $' + pastTrade1_Entry.close.toFixed(2) },
                { time: pastTrade1_Exit.time, position: 'aboveBar', color: '#089981', shape: 'arrowDown', text: 'TP CLOSE @ $' + pastTrade1_Exit.high.toFixed(2) },

                // Historical Trade 2 (LOSS / SL HIT)
                { time: pastTrade2_Entry.time, position: 'belowBar', color: '#089981', shape: 'arrowUp', text: 'BUY @ $' + pastTrade2_Entry.close.toFixed(2) },
                { time: pastTrade2_Exit.time, position: 'belowBar', color: '#F23645', shape: 'arrowDown', text: 'SL HIT @ $' + pastTrade2_Exit.low.toFixed(2) },

                // Current Active Trade Entry
                { time: currentTrade_Entry.time, position: 'belowBar', color: '#2962FF', shape: 'arrowUp', text: 'ACTIVE BUY @ $' + currentTrade_Entry.close.toFixed(2) }
            ];

            series.setMarkers(markers);

            // FVG Detection
            let fvg = null;
            for (let i = len - 35; i < len - 10; i++) {
                if (cdata[i].low > cdata[i - 2].high) {
                    fvg = { startTime: cdata[i - 2].time, top: cdata[i].low, bottom: cdata[i - 2].high };
                    break;
                }
            }

            stateObj.cdata = cdata;
            stateObj.fvg = fvg;
            stateObj.tradeHistory = [
                {
                    startTime: pastTrade1_Entry.time,
                    endTime: pastTrade1_Exit.time,
                    entryPrice: pastTrade1_Entry.close,
                    tpPrice: pastTrade1_Exit.high,
                    slPrice: pastTrade1_Entry.close * 0.992
                },
                {
                    startTime: pastTrade2_Entry.time,
                    endTime: pastTrade2_Exit.time,
                    entryPrice: pastTrade2_Entry.close,
                    tpPrice: pastTrade2_Entry.close * 1.015,
                    slPrice: pastTrade2_Exit.low
                },
                {
                    startTime: currentTrade_Entry.time,
                    endTime: cdata[len - 1].time,
                    entryPrice: currentTrade_Entry.close,
                    tpPrice: resPrice,
                    slPrice: supPrice
                }
            ];

            drawTradingViewMarkup(chart, series, canvasId, stateObj);
        }

        function fetchOHLCV(symbol, timeframe, chart, series, emaSeries, activeLines, canvasId, isFirstLoad, setFirstLoad, stateObj) {
            fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${timeframe}&limit=100`)
                .then(res => res.json())
                .then(data => {
                    const cdata = data.map(d => ({
                        time: Math.floor(d[0] / 1000),
                        open: parseFloat(d[1]),
                        high: parseFloat(d[2]),
                        low: parseFloat(d[3]),
                        close: parseFloat(d[4])
                    }));

                    if (isFirstLoad) {
                        series.setData(cdata);
                        applyICTStrategy(chart, series, emaSeries, cdata, activeLines, canvasId, stateObj);
                        setFirstLoad(false);
                    } else {
                        series.update(cdata[cdata.length - 1]);
                    }
                })
                .catch(err => console.error(`Error fetching ${symbol}:`, err));
        }

        function changeTF(asset, tf, btnElement) {
            const containerId = asset === 'BTC' ? 'tf-btc' : 'tf-xau';
            document.querySelectorAll(`#${containerId} .tf-btn`).forEach(b => b.classList.remove('active'));
            btnElement.classList.add('active');

            if (asset === 'BTC') {
                currentTF_BTC = tf;
                isFirstLoad_BTC = true;
            } else {
                currentTF_XAU = tf;
                isFirstLoad_XAU = true;
            }
            refreshAll();
        }

        function refreshAll() {
            fetchOHLCV('BTCUSDT', currentTF_BTC, chartBTC, seriesBTC, emaBTC, activeLines_BTC, 'canvas-btc', isFirstLoad_BTC, (v) => isFirstLoad_BTC = v, state_BTC);
            fetchOHLCV('PAXGUSDT', currentTF_XAU, chartXAU, seriesXAU, emaXAU, activeLines_XAU, 'canvas-xau', isFirstLoad_XAU, (v) => isFirstLoad_XAU = v, state_XAU);
        }

        chartBTC.timeScale().subscribeVisibleLogicalRangeChange(() => drawTradingViewMarkup(chartBTC, seriesBTC, 'canvas-btc', state_BTC));
        chartXAU.timeScale().subscribeVisibleLogicalRangeChange(() => drawTradingViewMarkup(chartXAU, seriesXAU, 'canvas-xau', state_XAU));

        refreshAll();
        setInterval(refreshAll, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000')
    app.run(port=5000)
