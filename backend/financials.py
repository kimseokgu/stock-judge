import re
import httpx
import yfinance as yf
from bs4 import BeautifulSoup

_NAVER_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get_financials(ticker: str) -> dict:
    code = ticker.replace(".KS", "").replace(".KQ", "").strip()
    is_korean = code.isdigit() and len(code) == 6

    if is_korean:
        return _get_korean_financials(code)
    else:
        return _get_us_financials(ticker)


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
        info = yf.Ticker(code + ".KS").info

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
    result = {
        "per": None, "pbr": None, "dividend_yield": None,
        "revenue_growth": None, "operating_margin": None, "gross_margin": None,
        "debt_ratio": None, "current_ratio": None,
        "roe": None, "roa": None, "eps_growth": None,
        "fcf_yield": None, "ev_ebitda": None, "week52_position": None,
    }

    try:
        info = yf.Ticker(ticker).info
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
