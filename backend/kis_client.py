import os
from datetime import date, timedelta
import httpx
import pandas as pd
from kis_auth import auth_headers

BASE_URL = os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")


def get_usd_krw() -> float:
    """USD/KRW 환율 조회 (yfinance)"""
    import yfinance as yf
    df = yf.download("USDKRW=X", period="1d", interval="1d", progress=False, auto_adjust=True)
    if df.empty:
        return 1350.0
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        val = close.iloc[-1, 0]
    else:
        val = close.iloc[-1]
    return float(val)


def is_korean(ticker: str) -> bool:
    """005930.KS 또는 005930 형태면 한국 주식"""
    code = ticker.replace(".KS", "").replace(".KQ", "")
    return code.isdigit() and len(code) == 6


def get_current_price(ticker: str) -> dict:
    """현재가 조회. 반환: {price, change_rate, volume}"""
    code = ticker.replace(".KS", "").replace(".KQ", "")
    if is_korean(ticker):
        url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code}
        headers = {**auth_headers(), "tr_id": "FHKST01010100"}
        resp = httpx.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        output = resp.json()["output"]
        return {
            "price": int(output["stck_prpr"]),
            "change_rate": float(output["prdy_ctrt"]),
            "volume": int(output["acml_vol"]),
        }
    else:
        try:
            url = f"{BASE_URL}/uapi/overseas-price/v1/quotations/price"
            params = {"AUTH": "", "EXCD": _get_exchange_code(ticker), "SYMB": ticker}
            headers = {**auth_headers(), "tr_id": "HHDFS00000300"}
            resp = httpx.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            output = resp.json()["output"]
            last = float(output.get("last", 0))
            if last > 0:
                rate = get_usd_krw()
                return {
                    "price": round(last * rate),
                    "change_rate": float(output.get("rate", 0)),
                    "volume": int(output.get("tvol", 0)),
                }
        except Exception:
            pass
        # yfinance 폴백 (KIS 해외 API 실패 시)
        import yfinance as yf
        info = yf.Ticker(ticker).fast_info
        rate = get_usd_krw()
        price = getattr(info, "last_price", None) or getattr(info, "previous_close", 0)
        return {
            "price": round(float(price) * rate),
            "change_rate": 0.0,
            "volume": getattr(info, "three_month_average_volume", 0) or 0,
        }


def get_daily_ohlcv(ticker: str, count: int = 120) -> pd.DataFrame:
    """yfinance로 일봉 OHLCV 데이터 조회 (기술적 지표 계산용)."""
    import yfinance as yf
    yf_ticker = _to_yf_ticker(ticker)
    df = yf.download(yf_ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
    if df.empty:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
    df = df.reset_index()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0].lower() for c in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]
    if "datetime" in df.columns:
        df = df.rename(columns={"datetime": "date"})
    df = df[["date", "open", "high", "low", "close", "volume"]]
    df = df.dropna(subset=["close", "open", "high", "low"]).tail(count).reset_index(drop=True)
    # 미국 주식은 원화로 변환
    if not is_korean(ticker):
        rate = get_usd_krw()
        for col in ["open", "high", "low", "close"]:
            df[col] = (df[col] * rate).round()
    return df


def _to_yf_ticker(ticker: str) -> str:
    """한국 주식 6자리 → .KS 붙임"""
    if "." in ticker:
        return ticker
    code = ticker.replace(".KS", "").replace(".KQ", "").strip()
    if code.isdigit() and len(code) == 6:
        return code + ".KS"
    return ticker


def _get_exchange_code(ticker: str) -> str:
    """미국 주식 거래소 코드 반환 (기본 NAS)"""
    return "NAS"
