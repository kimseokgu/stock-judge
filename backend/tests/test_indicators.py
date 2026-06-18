import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from indicators import calculate_indicators


def _make_df(closes: list[float]) -> pd.DataFrame:
    n = len(closes)
    return pd.DataFrame({
        "close": closes,
        "high": [c * 1.01 for c in closes],
        "low": [c * 0.99 for c in closes],
        "volume": [1_000_000] * n,
    })


def test_moving_averages_present():
    df = _make_df([100.0] * 100)
    result = calculate_indicators(df)
    assert "ma5" in result
    assert "ma20" in result
    assert "ma60" in result


def test_rsi_range():
    df = _make_df([float(i) for i in range(1, 101)])
    result = calculate_indicators(df)
    assert 0 <= result["rsi"] <= 100


def test_macd_keys_present():
    df = _make_df([float(100 + i % 10) for i in range(100)])
    result = calculate_indicators(df)
    assert "macd" in result
    assert "macd_signal" in result
    assert "macd_cross" in result


def test_bollinger_keys_present():
    df = _make_df([100.0] * 100)
    result = calculate_indicators(df)
    assert "bb_upper" in result
    assert "bb_lower" in result
    assert "bb_position" in result


def test_volume_ratio_present():
    df = _make_df([100.0] * 100)
    result = calculate_indicators(df)
    assert "volume_ratio" in result
