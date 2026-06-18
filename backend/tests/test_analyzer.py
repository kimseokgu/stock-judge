import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from analyzer import score_technical, score_financial, verdict


def test_perfect_technical_score():
    indicators = {
        "ma5": 110, "ma20": 105, "ma60": 100,
        "rsi": 40,
        "macd_cross": "golden",
        "bb_position": 0.1,
        "volume_ratio": 2.0,
    }
    assert score_technical(indicators) == 60


def test_worst_technical_score():
    indicators = {
        "ma5": 100, "ma20": 105, "ma60": 110,
        "rsi": 75,
        "macd_cross": "dead",
        "bb_position": 0.9,
        "volume_ratio": 0.3,
    }
    assert score_technical(indicators) == 0


def test_buy_verdict():
    assert verdict(75) == "buy"


def test_hold_verdict():
    assert verdict(55) == "hold"


def test_sell_verdict():
    assert verdict(30) == "sell"


def test_financial_score_good():
    financials = {
        "per": 10,
        "pbr": 0.8,
        "revenue_growth": 8,
        "operating_margin": 15,
        "debt_ratio": 80,
        "dividend_yield": 3,
    }
    assert score_financial(financials) == 40
