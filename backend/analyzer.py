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


def reasons(indicators: dict, financials: dict) -> list[str]:
    out = []
    ind, fin = indicators, financials

    ma5, ma20, ma60 = ind.get("ma5"), ind.get("ma20"), ind.get("ma60")
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            out.append("이동평균 정배열 — 단기·중기·장기 모두 상승 추세")
        elif ma5 < ma20 < ma60:
            out.append("이동평균 역배열 — 하락 추세 진행 중")

    rsi = ind.get("rsi")
    if rsi is not None:
        if rsi < 30:
            out.append(f"RSI {rsi:.0f} — 과매도 구간, 반등 가능성")
        elif rsi >= 70:
            out.append(f"RSI {rsi:.0f} — 과매수 구간, 조정 주의")
        elif 30 <= rsi <= 50:
            out.append(f"RSI {rsi:.0f} — 저점 매수 구간")

    cross = ind.get("macd_cross")
    if cross == "golden":
        out.append("MACD 골든크로스 — 상승 전환 신호")
    elif cross == "dead":
        out.append("MACD 데드크로스 — 하락 전환 신호")

    bb = ind.get("bb_position")
    if bb is not None:
        if bb <= 0.2:
            out.append(f"볼린저밴드 하단 근접 (위치 {bb:.2f}) — 반등 구간")
        elif bb >= 0.8:
            out.append(f"볼린저밴드 상단 근접 (위치 {bb:.2f}) — 과열 주의")

    per = fin.get("per")
    if per:
        if per <= 15:
            out.append(f"PER {per:.1f} — 저평가 구간")
        elif per > 30:
            out.append(f"PER {per:.1f} — 고평가 주의")

    rg = fin.get("revenue_growth")
    if rg is not None:
        if rg >= 10:
            out.append(f"매출 성장률 {rg:.1f}% — 강한 성장세")
        elif rg < 0:
            out.append(f"매출 성장률 {rg:.1f}% — 매출 감소 중")

    om = fin.get("operating_margin")
    if om is not None:
        if om < 0:
            out.append(f"영업이익률 {om:.1f}% — 적자 기업")
        elif om >= 15:
            out.append(f"영업이익률 {om:.1f}% — 높은 수익성")

    if not out:
        out.append("특이 신호 없음 — 중립 상태")

    return out


def analyze(indicators: dict, financials: dict) -> dict:
    tech_score = score_technical(indicators)
    fin_score = score_financial(financials)
    total = tech_score + fin_score
    return {
        "verdict": verdict(total),
        "total_score": total,
        "technical_score": tech_score,
        "financial_score": fin_score,
        "reasons": reasons(indicators, financials),
    }
