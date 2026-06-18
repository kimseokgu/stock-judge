"""
점수 체계: 기술적 40pt + 재무 60pt = 100pt
매수: 65점 이상 / 보류: 40~64점 / 매도: 39점 이하
"""


def score_technical(ind: dict) -> int:
    score = 0

    # 이동평균 (12pt)
    ma5, ma20, ma60 = ind.get("ma5"), ind.get("ma20"), ind.get("ma60")
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            score += 12
        elif ma5 > ma20 or ma20 > ma60:
            score += 6
    elif ma5 and ma20:
        if ma5 > ma20:
            score += 8

    # RSI (10pt)
    rsi = ind.get("rsi", 50)
    if 30 <= rsi <= 50:
        score += 10
    elif 50 < rsi <= 60:
        score += 5
    elif rsi < 30:
        score += 4

    # MACD (10pt)
    cross = ind.get("macd_cross", "none")
    if cross == "golden":
        score += 10
    elif cross == "none":
        score += 4

    # 볼린저밴드 (5pt)
    bb_pos = ind.get("bb_position", 0.5)
    if bb_pos <= 0.2:
        score += 5
    elif bb_pos <= 0.4:
        score += 2

    # 거래량 (3pt)
    vol_ratio = ind.get("volume_ratio", 1.0)
    if vol_ratio >= 1.5:
        score += 3
    elif vol_ratio >= 1.0:
        score += 1

    return score  # 최대 40pt


def score_financial(fin: dict) -> int:
    score = 0

    # ── 밸류에이션 ──────────────────────────
    # PER (8pt)
    per = fin.get("per")
    if per and 0 < per <= 10:
        score += 8
    elif per and per <= 15:
        score += 6
    elif per and per <= 25:
        score += 3

    # EV/EBITDA (7pt): 10 이하 우량
    ev_eb = fin.get("ev_ebitda")
    if ev_eb and 0 < ev_eb <= 8:
        score += 7
    elif ev_eb and ev_eb <= 12:
        score += 4
    elif ev_eb and ev_eb <= 18:
        score += 2

    # PBR (5pt)
    pbr = fin.get("pbr")
    if pbr and 0 < pbr <= 1:
        score += 5
    elif pbr and pbr <= 2:
        score += 2

    # ── 수익성 ──────────────────────────────
    # ROE (10pt): 15% 이상이면 우량
    roe = fin.get("roe")
    if roe and roe >= 20:
        score += 10
    elif roe and roe >= 15:
        score += 7
    elif roe and roe >= 10:
        score += 4
    elif roe and roe < 0:
        score -= 3  # 적자

    # ROA (5pt): 5% 이상
    roa = fin.get("roa")
    if roa and roa >= 8:
        score += 5
    elif roa and roa >= 5:
        score += 3
    elif roa and roa >= 2:
        score += 1

    # 영업이익률 (5pt)
    op_margin = fin.get("operating_margin")
    if op_margin and op_margin >= 20:
        score += 5
    elif op_margin and op_margin >= 10:
        score += 3
    elif op_margin and op_margin >= 5:
        score += 1
    elif op_margin and op_margin < 0:
        score -= 2

    # 매출총이익률 (3pt)
    gm = fin.get("gross_margin")
    if gm and gm >= 40:
        score += 3
    elif gm and gm >= 20:
        score += 1

    # ── 성장성 ──────────────────────────────
    # 매출 성장률 (5pt)
    rev = fin.get("revenue_growth")
    if rev and rev >= 20:
        score += 5
    elif rev and rev >= 10:
        score += 3
    elif rev and rev >= 5:
        score += 1
    elif rev and rev < -5:
        score -= 2

    # EPS 성장률 (5pt)
    eps_g = fin.get("eps_growth")
    if eps_g and eps_g >= 20:
        score += 5
    elif eps_g and eps_g >= 10:
        score += 3
    elif eps_g and eps_g >= 0:
        score += 1
    elif eps_g and eps_g < -10:
        score -= 2

    # ── 재무 건전성 ─────────────────────────
    # FCF Yield (4pt): 양수면 실제로 현금 창출
    fcf = fin.get("fcf_yield")
    if fcf and fcf >= 5:
        score += 4
    elif fcf and fcf >= 2:
        score += 2
    elif fcf and fcf >= 0:
        score += 1
    elif fcf and fcf < 0:
        score -= 2

    # 유동비율 (3pt): 1.5 이상이면 단기 안전
    cr = fin.get("current_ratio")
    if cr and cr >= 2.0:
        score += 3
    elif cr and cr >= 1.5:
        score += 2
    elif cr and cr >= 1.0:
        score += 1

    # 부채비율 (3pt)
    debt = fin.get("debt_ratio")
    if debt and debt <= 50:
        score += 3
    elif debt and debt <= 100:
        score += 2
    elif debt and debt <= 200:
        score += 1
    elif debt and debt > 300:
        score -= 1

    # 배당수익률 (2pt)
    div = fin.get("dividend_yield")
    if div and div >= 3:
        score += 2
    elif div and div >= 1.5:
        score += 1

    return max(score, 0)  # 최대 60pt, 최소 0


def verdict(total_score: int) -> str:
    if total_score >= 65:
        return "buy"
    elif total_score >= 40:
        return "hold"
    else:
        return "sell"


def reasons(indicators: dict, financials: dict) -> list[str]:
    out = []
    ind, fin = indicators, financials

    # 기술적
    ma5, ma20, ma60 = ind.get("ma5"), ind.get("ma20"), ind.get("ma60")
    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            out.append("📈 이동평균 정배열 — 단기·중기·장기 모두 상승 추세")
        elif ma5 < ma20 < ma60:
            out.append("📉 이동평균 역배열 — 하락 추세 진행 중")

    rsi = ind.get("rsi")
    if rsi is not None:
        if rsi < 30:
            out.append(f"🟢 RSI {rsi:.0f} — 과매도 구간, 반등 가능성")
        elif rsi >= 70:
            out.append(f"🔴 RSI {rsi:.0f} — 과매수 구간, 조정 주의")
        elif 30 <= rsi <= 50:
            out.append(f"🟢 RSI {rsi:.0f} — 저점 매수 구간")

    cross = ind.get("macd_cross")
    if cross == "golden":
        out.append("🟢 MACD 골든크로스 — 상승 전환 신호")
    elif cross == "dead":
        out.append("🔴 MACD 데드크로스 — 하락 전환 신호")

    bb = ind.get("bb_position")
    if bb is not None:
        if bb <= 0.2:
            out.append(f"🟢 볼린저밴드 하단 근접 ({bb:.2f}) — 반등 구간")
        elif bb >= 0.8:
            out.append(f"🔴 볼린저밴드 상단 근접 ({bb:.2f}) — 과열 주의")

    # 밸류에이션
    per = fin.get("per")
    if per:
        if per <= 10:
            out.append(f"🟢 PER {per:.1f} — 매우 저평가")
        elif per <= 15:
            out.append(f"🟢 PER {per:.1f} — 저평가 구간")
        elif per > 30:
            out.append(f"🔴 PER {per:.1f} — 고평가 주의")

    ev_eb = fin.get("ev_ebitda")
    if ev_eb:
        if ev_eb <= 8:
            out.append(f"🟢 EV/EBITDA {ev_eb:.1f} — 저평가 (8 이하 우량)")
        elif ev_eb > 20:
            out.append(f"🔴 EV/EBITDA {ev_eb:.1f} — 고평가 구간")

    pbr = fin.get("pbr")
    if pbr:
        if pbr <= 1:
            out.append(f"🟢 PBR {pbr:.2f} — 순자산 대비 저평가")
        elif pbr > 4:
            out.append(f"🔴 PBR {pbr:.2f} — 순자산 대비 고평가")

    # 수익성
    roe = fin.get("roe")
    if roe is not None:
        if roe >= 15:
            out.append(f"🟢 ROE {roe:.1f}% — 자본 효율성 우수")
        elif roe < 0:
            out.append(f"🔴 ROE {roe:.1f}% — 자본 손실 중 (적자)")

    roa = fin.get("roa")
    if roa is not None:
        if roa >= 5:
            out.append(f"🟢 ROA {roa:.1f}% — 자산 대비 수익성 양호")
        elif roa < 0:
            out.append(f"🔴 ROA {roa:.1f}% — 자산 수익률 마이너스")

    om = fin.get("operating_margin")
    if om is not None:
        if om >= 20:
            out.append(f"🟢 영업이익률 {om:.1f}% — 높은 수익성")
        elif om < 0:
            out.append(f"🔴 영업이익률 {om:.1f}% — 영업 적자")

    # 성장성
    rg = fin.get("revenue_growth")
    if rg is not None:
        if rg >= 20:
            out.append(f"🟢 매출 성장률 {rg:.1f}% — 고성장 기업")
        elif rg >= 10:
            out.append(f"🟢 매출 성장률 {rg:.1f}% — 견고한 성장세")
        elif rg < -5:
            out.append(f"🔴 매출 성장률 {rg:.1f}% — 매출 감소 중")

    eps_g = fin.get("eps_growth")
    if eps_g is not None:
        if eps_g >= 20:
            out.append(f"🟢 EPS 성장률 {eps_g:.1f}% — 이익 고성장")
        elif eps_g < -10:
            out.append(f"🔴 EPS 성장률 {eps_g:.1f}% — 이익 급감")

    # 재무 건전성
    fcf = fin.get("fcf_yield")
    if fcf is not None:
        if fcf >= 5:
            out.append(f"🟢 FCF 수익률 {fcf:.1f}% — 현금 창출력 우수")
        elif fcf < 0:
            out.append(f"🔴 FCF 수익률 {fcf:.1f}% — 잉여현금흐름 마이너스")

    debt = fin.get("debt_ratio")
    if debt is not None:
        if debt > 300:
            out.append(f"🔴 부채비율 {debt:.0f}% — 재무 위험 높음")
        elif debt <= 50:
            out.append(f"🟢 부채비율 {debt:.0f}% — 재무 구조 매우 안전")

    cr = fin.get("current_ratio")
    if cr is not None:
        if cr < 1.0:
            out.append(f"🔴 유동비율 {cr:.2f} — 단기 유동성 위험")
        elif cr >= 2.0:
            out.append(f"🟢 유동비율 {cr:.2f} — 단기 재무 안전")

    w52 = fin.get("week52_position")
    if w52 is not None:
        if w52 <= 0.2:
            out.append(f"🟢 52주 저점 근접 ({w52:.0%}) — 저점 매수 기회")
        elif w52 >= 0.9:
            out.append(f"🔴 52주 고점 근접 ({w52:.0%}) — 고점 추격 주의")

    if not out:
        out.append("⚪ 특이 신호 없음 — 중립 상태")

    return out


def analyze(indicators: dict, financials: dict) -> dict:
    tech_score = score_technical(indicators)
    fin_score = score_financial(financials)
    total = min(tech_score + fin_score, 100)
    return {
        "verdict": verdict(total),
        "total_score": total,
        "technical_score": tech_score,
        "financial_score": fin_score,
        "reasons": reasons(indicators, financials),
    }
