import pandas as pd
import ta


def calculate_indicators(df: pd.DataFrame) -> dict:
    """
    df 컬럼: close, high, low, volume (최소 60행 권장)
    반환: 지표 딕셔너리
    """
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"]

    # 이동평균
    ma5 = close.rolling(5).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    ma60 = close.rolling(60).mean().iloc[-1] if len(df) >= 60 else None

    # RSI
    rsi_indicator = ta.momentum.RSIIndicator(close, window=14)
    rsi = rsi_indicator.rsi().iloc[-1]

    # MACD
    macd_ind = ta.trend.MACD(close)
    macd_val = macd_ind.macd().iloc[-1]
    macd_sig = macd_ind.macd_signal().iloc[-1]
    prev_macd = macd_ind.macd().iloc[-2]
    prev_sig = macd_ind.macd_signal().iloc[-2]

    if prev_macd < prev_sig and macd_val > macd_sig:
        macd_cross = "golden"
    elif prev_macd > prev_sig and macd_val < macd_sig:
        macd_cross = "dead"
    else:
        macd_cross = "none"

    # 볼린저밴드
    bb = ta.volatility.BollingerBands(close, window=20)
    bb_upper = bb.bollinger_hband().iloc[-1]
    bb_lower = bb.bollinger_lband().iloc[-1]
    current_price = close.iloc[-1]
    bb_range = bb_upper - bb_lower
    bb_position = (current_price - bb_lower) / bb_range if bb_range > 0 else 0.5

    # 거래량 비율 (최근 1일 / 20일 평균)
    vol_avg20 = volume.rolling(20).mean().iloc[-1]
    vol_ratio = volume.iloc[-1] / vol_avg20 if vol_avg20 > 0 else 1.0

    return {
        "ma5": round(float(ma5), 2) if ma5 is not None else None,
        "ma20": round(float(ma20), 2) if ma20 is not None else None,
        "ma60": round(float(ma60), 2) if ma60 is not None else None,
        "rsi": round(float(rsi), 2),
        "macd": round(float(macd_val), 4),
        "macd_signal": round(float(macd_sig), 4),
        "macd_cross": macd_cross,
        "bb_upper": round(float(bb_upper), 2),
        "bb_lower": round(float(bb_lower), 2),
        "bb_position": round(float(bb_position), 4),
        "volume_ratio": round(float(vol_ratio), 2),
    }
