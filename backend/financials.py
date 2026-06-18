import re
import httpx
import yfinance as yf
from bs4 import BeautifulSoup

_NAVER_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get_financials(ticker: str) -> dict:
    """
    한국 주식: 네이버 금융 크롤링 (PER, PBR) + yfinance (나머지)
    미국 주식: yfinance 전체
    반환: {per, pbr, dividend_yield, revenue_growth, operating_margin, debt_ratio}
    """
    code = ticker.replace(".KS", "").replace(".KQ", "").strip()
    is_korean = code.isdigit() and len(code) == 6

    if is_korean:
        return _get_korean_financials(code)
    else:
        return _get_us_financials(ticker)


def _get_korean_financials(code: str) -> dict:
    """네이버 금융에서 한국 주식 재무 데이터 크롤링."""
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
        dividend_yield = div_raw  # 이미 % 단위

    except Exception:
        pass

    # yfinance에서 나머지 재무 데이터 시도 (없으면 None)
    revenue_growth, operating_margin, debt_ratio = None, None, None
    try:
        info = yf.Ticker(code + ".KS").info
        rg = info.get("revenueGrowth")
        if rg:
            revenue_growth = round(rg * 100, 2)
        om = info.get("operatingMargins")
        if om:
            operating_margin = round(om * 100, 2)
        total_debt = info.get("totalDebt")
        equity = info.get("totalStockholderEquity")
        if total_debt is not None and equity and equity > 0:
            debt_ratio = round(total_debt / equity * 100, 2)
    except Exception:
        pass

    return {
        "per": round(per, 2) if per else None,
        "pbr": round(pbr, 2) if pbr else None,
        "dividend_yield": round(dividend_yield, 2) if dividend_yield else None,
        "revenue_growth": revenue_growth,
        "operating_margin": operating_margin,
        "debt_ratio": debt_ratio,
    }


def _get_us_financials(ticker: str) -> dict:
    """yfinance로 미국 주식 재무 데이터 조회."""
    info = yf.Ticker(ticker).info

    per = info.get("trailingPE")
    pbr = info.get("priceToBook")

    dividend_yield = info.get("dividendYield")
    if dividend_yield:
        dividend_yield = round(dividend_yield * 100, 2)

    revenue_growth = info.get("revenueGrowth")
    if revenue_growth:
        revenue_growth = round(revenue_growth * 100, 2)

    operating_margin = info.get("operatingMargins")
    if operating_margin:
        operating_margin = round(operating_margin * 100, 2)

    total_debt = info.get("totalDebt")
    equity = info.get("totalStockholderEquity")
    if total_debt is not None and equity and equity > 0:
        debt_ratio = round(total_debt / equity * 100, 2)
    else:
        debt_ratio = None

    return {
        "per": round(per, 2) if per else None,
        "pbr": round(pbr, 2) if pbr else None,
        "dividend_yield": dividend_yield,
        "revenue_growth": revenue_growth,
        "operating_margin": operating_margin,
        "debt_ratio": debt_ratio,
    }
