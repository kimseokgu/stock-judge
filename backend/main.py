import json
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from kis_client import get_current_price, get_daily_ohlcv
from indicators import calculate_indicators
from financials import get_financials
from analyzer import analyze
from kis_ws import stream_price
from stock_list import search_stocks, STOCKS

_TICKER_NAME = {s["ticker"]: s["name"] for s in STOCKS}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WATCHLIST_FILE = Path(__file__).parent / "watchlist.json"


def load_watchlist() -> list[str]:
    if WATCHLIST_FILE.exists():
        return json.loads(WATCHLIST_FILE.read_text(encoding="utf-8"))
    return ["AAPL", "005930"]


def save_watchlist(stocks: list[str]):
    WATCHLIST_FILE.write_text(json.dumps(stocks, ensure_ascii=False), encoding="utf-8")


# ── 종목 리스트 API ──────────────────────────────
@app.get("/watchlist")
def get_watchlist():
    tickers = load_watchlist()
    return [{"ticker": t, "name": _TICKER_NAME.get(t, t)} for t in tickers]


@app.post("/watchlist/{ticker}")
def add_to_watchlist(ticker: str):
    stocks = load_watchlist()
    if ticker not in stocks:
        stocks.append(ticker)
        save_watchlist(stocks)
    return [{"ticker": t, "name": _TICKER_NAME.get(t, t)} for t in stocks]


@app.delete("/watchlist/{ticker}")
def remove_from_watchlist(ticker: str):
    stocks = load_watchlist()
    stocks = [s for s in stocks if s != ticker]
    save_watchlist(stocks)
    return [{"ticker": t, "name": _TICKER_NAME.get(t, t)} for t in stocks]


# ── 검색 & 분석 ──────────────────────────────────
@app.get("/search")
def search(q: str = ""):
    return search_stocks(q)


@app.get("/chart/{ticker}")
def chart_data(ticker: str, period: str = "3m"):
    period_map = {"1w": 5, "1m": 21, "3m": 63, "1y": 120}
    count = period_map.get(period, 63)
    df = get_daily_ohlcv(ticker, count=120)
    df = df.tail(count)
    return [
        {"date": str(row["date"])[:10], "close": float(row["close"])}
        for _, row in df.iterrows()
    ]


@app.get("/analyze/{ticker}")
def analyze_ticker(ticker: str):
    import traceback
    try:
        df = get_daily_ohlcv(ticker)
        ind = calculate_indicators(df)
        fin = get_financials(ticker)
        result = analyze(ind, fin)
        current = get_current_price(ticker)
    except Exception as e:
        return {"error": str(e), "detail": traceback.format_exc()}
    return {
        "ticker": ticker,
        "name": _TICKER_NAME.get(ticker, ticker),
        "current": current,
        "verdict": result["verdict"],
        "total_score": result["total_score"],
        "technical_score": result["technical_score"],
        "financial_score": result["financial_score"],
        "reasons": result["reasons"],
        "indicators": ind,
        "financials": fin,
    }


@app.get("/debug/fin/{ticker}")
def debug_fin(ticker: str):
    import traceback
    from financials import _yf_info
    try:
        info = _yf_info(ticker)
        keys = ["trailingPE","priceToBook","returnOnEquity","returnOnAssets",
                "revenueGrowth","operatingMargins","grossMargins","earningsGrowth",
                "freeCashflow","marketCap","currentRatio","enterpriseToEbitda",
                "totalDebt","totalStockholderEquity"]
        return {k: info.get(k) for k in keys}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}


@app.get("/price/{ticker}")
def current_price(ticker: str):
    try:
        return get_current_price(ticker)
    except Exception as e:
        return {"error": str(e)}


@app.websocket("/ws/{ticker}")
async def ws_price(websocket: WebSocket, ticker: str):
    await websocket.accept()
    try:
        await stream_price(ticker, websocket)
    except WebSocketDisconnect:
        pass


# ── 프론트엔드 서빙 (마지막에 선언) ──────────────
FRONTEND_DIR = Path(__file__).parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
