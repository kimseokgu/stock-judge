def score_technical(ind: dict) -> int:
    score = 0

    # 이동평균 (20점): 정배열이면 만점
    ma5, ma20, ma60 = ind.get("ma5"), ind.get("ma20"), ind.get("ma60")
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            score += 20
        elif ma5 > ma20 or ma20 > ma60:
            score += 10
    elif ma5 and ma20:
        if ma5 > ma20:
            score += 15

    # RSI (15점)
    rsi = ind.get("rsi", 50)
    if 30 <= rsi <= 50:
        score += 15
    elif 50 < rsi <= 60:
        score += 8
    elif rsi < 30:
        score += 5

    # MACD (15점)
    cross = ind.get("macd_cross", "none")
    if cross == "golden":
        score += 15
    elif cross == "none":
        score += 7

    # 볼린저밴드 (5점): 하단 근처(0~0.2)면 만점
    bb_pos = ind.get("bb_position", 0.5)
    if bb_pos <= 0.2:
        score += 5
    elif bb_pos <= 0.4:
        score += 3

    # 거래량 (5점): 평균 대비 1.5배 이상 급증
    vol_ratio = ind.get("volume_ratio", 1.0)
    if vol_ratio >= 1.5:
        score += 5
    elif vol_ratio >= 1.0:
        score += 2

    return score


def score_financial(fin: dict) -> int:
    score = 0

    # PER (10점): 15 이하
    per = fin.get("per")
    if per and per <= 15:
        score += 10
    elif per and per <= 25:
        score += 5

    # PBR (8점): 1 이하
    pbr = fin.get("pbr")
    if pbr and pbr <= 1:
        score += 8
    elif pbr and pbr <= 2:
        score += 4

    # 매출성장률 (8점): 5% 이상
    rev_growth = fin.get("revenue_growth")
    if rev_growth and rev_growth >= 5:
        score += 8
    elif rev_growth and rev_growth >= 0:
        score += 4

    # 영업이익률 (7점): 10% 이상
    op_margin = fin.get("operating_margin")
    if op_margin and op_margin >= 10:
        score += 7
    elif op_margin and op_margin >= 5:
        score += 3

    # 부채비율 (4점): 100% 이하
    debt = fin.get("debt_ratio")
    if debt and debt <= 100:
        score += 4
    elif debt and debt <= 200:
        score += 2

    # 배당수익률 (3점): 2% 이상
    div = fin.get("dividend_yield")
    if div and div >= 2:
        score += 3
    elif div and div >= 1:
        score += 1

    return score


def verdict(total_score: int) -> str:
    if total_score >= 70:
        return "buy"
    elif total_score >= 40:
        return "hold"
    else:
        return "sell"


def analyze(indicators: dict, financials: dict) -> dict:
    tech_score = score_technical(indicators)
    fin_score = score_financial(financials)
    total = tech_score + fin_score
    return {
        "verdict": verdict(total),
        "total_score": total,
        "technical_score": tech_score,
        "financial_score": fin_score,
    }
