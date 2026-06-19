import re
import time
import json
import httpx
import yfinance as yf
from pathlib import Path
from bs4 import BeautifulSoup

_NAVER_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
_CACHE_FILE = Path(__file__).parent / "fin_cache.json"
_CACHE_TTL = 24 * 3600  # 24시간


def _load_cache() -> dict:
    try:
        if _CACHE_FILE.exists():
            return json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_cache(cache: dict):
    try:
        _CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def _finnhub_us_financials(ticker: str) -> dict:
    """Finnhub API로 미국 주식 재무지표 조회."""
    import os
    api_key = os.getenv("FINNHUB_API_KEY", "")
    if not api_key:
        return {}
    try:
        resp = httpx.get(
            "https://finnhub.io/api/v1/stock/metric",
            params={"symbol": ticker, "metric": "all", "token": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        m = resp.json().get("metric", {})
        if not m:
            return {}

        result = {}

        per = m.get("peBasicExclExtraTTM") or m.get("peNormalizedAnnual")
        if per and per > 0:
            result["per"] = round(per, 2)

        pbr = m.get("pbAnnual")
        if pbr and pbr > 0:
            result["pbr"] = round(pbr, 2)

        roe = m.get("roeTTM") or m.get("roeAnnual")
        if roe is not None:
            result["roe"] = round(roe, 2)

        roa = m.get("roaTTM") or m.get("roaAnnual")
        if roa is not None:
            result["roa"] = round(roa, 2)

        rg = m.get("revenueGrowthTTMYoy")
        if rg is not None:
            result["revenue_growth"] = round(rg, 2)

        eps_g = m.get("epsGrowthTTMYoy")
        if eps_g is not None:
            result["eps_growth"] = round(eps_g, 2)

        om = m.get("operatingMarginAnnual")
        if om is not None:
            result["operating_margin"] = round(om, 2)

        gm = m.get("grossMarginAnnual") or m.get("grossMarginTTM")
        if gm is not None:
            result["gross_margin"] = round(gm, 2)

        div = m.get("dividendYieldIndicatedAnnual")
        if div:
            result["dividend_yield"] = round(div, 2)

        cr = m.get("currentRatioAnnual") or m.get("currentRatioQuarterly")
        if cr is not None:
            result["current_ratio"] = round(cr, 2)

        # 부채비율 = 총부채 / 자기자본
        ltd = m.get("longTermDebt/equityAnnual")
        if ltd is not None:
            result["debt_ratio"] = round(ltd, 2)

        ev_eb = m.get("enterpriseValueEbitdaTTM")
        if ev_eb and ev_eb > 0:
            result["ev_ebitda"] = round(ev_eb, 2)

        # FCF yield
        fcf = m.get("freeCashFlowAnnual")
        mktcap = m.get("marketCapitalization")
        if fcf is not None and mktcap and mktcap > 0:
            result["fcf_yield"] = round(fcf / mktcap * 100, 2)

        # 52주 위치
        hi52 = m.get("52WeekHigh")
        lo52 = m.get("52WeekLow")
        # fast_info로 현재가
        try:
            fi = yf.Ticker(ticker).fast_info
            price = getattr(fi, "last_price", None) or getattr(fi, "previous_close", 0)
            if hi52 and lo52 and price and hi52 > lo52:
                result["week52_position"] = round((price - lo52) / (hi52 - lo52), 2)
        except Exception:
            pass

        return result
    except Exception:
        return {}


def get_financials(ticker: str) -> dict:
    cache = _load_cache()
    now = time.time()
    if ticker in cache and now - cache[ticker]["ts"] < _CACHE_TTL:
        return cache[ticker]["data"]

    code = ticker.replace(".KS", "").replace(".KQ", "").strip()
    is_korean = code.isdigit() and len(code) == 6

    data = _get_korean_financials(code) if is_korean else _get_us_financials(ticker)

    cache[ticker] = {"ts": now, "data": data}
    _save_cache(cache)
    return data


def _get_korean_financials(code: str) -> dict:
    per, pbr, dividend_yield = None, None, None

    try:
        resp = httpx.get(
            f"https://finance.naver.com/item/main.naver?code={code}",
            headers=_NAVER_HEADERS, timeout=10, follow_redirects=True
        )
        soup = BeautifulSoup(resp.text, "html.parser")

        def parse_val(label: str):
            th = soup.find("strong", string=re.compile(label))
            if th:
                td = th.find_parent("th").find_next_sibling("td")
                if td:
                    txt = td.get_text(strip=True).replace(",", "")
                    try:
                        return float(txt)
                    except ValueError:
                        return None
            return None

        per = parse_val("PER")
        pbr = parse_val("PBR")
        div_raw = parse_val("배당수익률")
        dividend_yield = div_raw
    except Exception:
        pass

    # yfinance로 나머지 재무 데이터
    result = {
        "per": round(per, 2) if per else None,
        "pbr": round(pbr, 2) if pbr else None,
        "dividend_yield": round(dividend_yield, 2) if dividend_yield else None,
        "revenue_growth": None,
        "operating_margin": None,
        "gross_margin": None,
        "debt_ratio": None,
        "current_ratio": None,
        "roe": None,
        "roa": None,
        "eps_growth": None,
        "fcf_yield": None,
        "ev_ebitda": None,
        "week52_position": None,
    }

    try:
        info = _yf_info(code + ".KS")

        def pct_field(key):
            v = info.get(key)
            return round(v * 100, 2) if v is not None else None

        result["revenue_growth"] = pct_field("revenueGrowth")
        result["operating_margin"] = pct_field("operatingMargins")
        result["gross_margin"] = pct_field("grossMargins")
        result["roe"] = pct_field("returnOnEquity")
        result["roa"] = pct_field("returnOnAssets")
        result["eps_growth"] = pct_field("earningsGrowth")

        total_debt = info.get("totalDebt")
        equity = info.get("totalStockholderEquity")
        if total_debt is not None and equity and equity > 0:
            result["debt_ratio"] = round(total_debt / equity * 100, 2)

        cr = info.get("currentRatio")
        if cr is not None:
            result["current_ratio"] = round(cr, 2)

        fcf = info.get("freeCashflow")
        mktcap = info.get("marketCap")
        if fcf and mktcap and mktcap > 0:
            result["fcf_yield"] = round(fcf / mktcap * 100, 2)

        ev_eb = info.get("enterpriseToEbitda")
        if ev_eb and ev_eb > 0:
            result["ev_ebitda"] = round(ev_eb, 2)

        hi52 = info.get("fiftyTwoWeekHigh")
        lo52 = info.get("fiftyTwoWeekLow")
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if hi52 and lo52 and price and hi52 > lo52:
            result["week52_position"] = round((price - lo52) / (hi52 - lo52), 2)

        if result["per"] is None:
            v = info.get("trailingPE")
            if v:
                result["per"] = round(v, 2)
        if result["pbr"] is None:
            v = info.get("priceToBook")
            if v:
                result["pbr"] = round(v, 2)
    except Exception:
        pass

    return result


def _get_us_financials(ticker: str) -> dict:
    _empty = {
        "per": None, "pbr": None, "dividend_yield": None,
        "revenue_growth": None, "operating_margin": None, "gross_margin": None,
        "debt_ratio": None, "current_ratio": None,
        "roe": None, "roa": None, "eps_growth": None,
        "fcf_yield": None, "ev_ebitda": None, "week52_position": None,
    }

    # Finnhub 우선 (cloud에서 yfinance .info가 rate limit으로 차단됨)
    finnhub = _finnhub_us_financials(ticker)
    if finnhub:
        return {**_empty, **finnhub}

    # fallback: yfinance .info (로컬에서만 동작)
    result = dict(_empty)
    try:
        info = _yf_info(ticker)
    except Exception:
        return result

    def pct_field(key):
        v = info.get(key)
        return round(v * 100, 2) if v is not None else None

    result["per"] = round(info["trailingPE"], 2) if info.get("trailingPE") else None
    result["pbr"] = round(info["priceToBook"], 2) if info.get("priceToBook") else None
    result["revenue_growth"] = pct_field("revenueGrowth")
    result["operating_margin"] = pct_field("operatingMargins")
    result["gross_margin"] = pct_field("grossMargins")
    result["roe"] = pct_field("returnOnEquity")
    result["roa"] = pct_field("returnOnAssets")
    result["eps_growth"] = pct_field("earningsGrowth")

    div = info.get("dividendYield")
    if div:
        result["dividend_yield"] = round(div * 100, 2)

    total_debt = info.get("totalDebt")
    equity = info.get("totalStockholderEquity")
    if total_debt is not None and equity and equity > 0:
        result["debt_ratio"] = round(total_debt / equity * 100, 2)

    cr = info.get("currentRatio")
    if cr is not None:
        result["current_ratio"] = round(cr, 2)

    fcf = info.get("freeCashflow")
    mktcap = info.get("marketCap")
    if fcf and mktcap and mktcap > 0:
        result["fcf_yield"] = round(fcf / mktcap * 100, 2)

    ev_eb = info.get("enterpriseToEbitda")
    if ev_eb and ev_eb > 0:
        result["ev_ebitda"] = round(ev_eb, 2)

    hi52 = info.get("fiftyTwoWeekHigh")
    lo52 = info.get("fiftyTwoWeekLow")
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    if hi52 and lo52 and price and hi52 > lo52:
        result["week52_position"] = round((price - lo52) / (hi52 - lo52), 2)

    return result
