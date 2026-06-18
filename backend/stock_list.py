# 주요 한국/미국 주식 목록 (이름 → 티커)
STOCKS = [
    # 한국 대형주
    {"name": "삼성전자", "ticker": "005930", "market": "KR"},
    {"name": "SK하이닉스", "ticker": "000660", "market": "KR"},
    {"name": "LG에너지솔루션", "ticker": "373220", "market": "KR"},
    {"name": "삼성바이오로직스", "ticker": "207940", "market": "KR"},
    {"name": "현대차", "ticker": "005380", "market": "KR"},
    {"name": "셀트리온", "ticker": "068270", "market": "KR"},
    {"name": "기아", "ticker": "000270", "market": "KR"},
    {"name": "KB금융", "ticker": "105560", "market": "KR"},
    {"name": "신한지주", "ticker": "055550", "market": "KR"},
    {"name": "POSCO홀딩스", "ticker": "005490", "market": "KR"},
    {"name": "LG화학", "ticker": "051910", "market": "KR"},
    {"name": "삼성SDI", "ticker": "006400", "market": "KR"},
    {"name": "카카오", "ticker": "035720", "market": "KR"},
    {"name": "네이버", "ticker": "035420", "market": "KR"},
    {"name": "카카오뱅크", "ticker": "323410", "market": "KR"},
    {"name": "하나금융지주", "ticker": "086790", "market": "KR"},
    {"name": "삼성물산", "ticker": "028260", "market": "KR"},
    {"name": "LG전자", "ticker": "066570", "market": "KR"},
    {"name": "현대모비스", "ticker": "012330", "market": "KR"},
    {"name": "SK텔레콤", "ticker": "017670", "market": "KR"},
    {"name": "KT", "ticker": "030200", "market": "KR"},
    {"name": "두산에너빌리티", "ticker": "034020", "market": "KR"},
    {"name": "한국전력", "ticker": "015760", "market": "KR"},
    {"name": "삼성전기", "ticker": "009150", "market": "KR"},
    {"name": "SK이노베이션", "ticker": "096770", "market": "KR"},
    {"name": "롯데케미칼", "ticker": "011170", "market": "KR"},
    {"name": "크래프톤", "ticker": "259960", "market": "KR"},
    {"name": "엔씨소프트", "ticker": "036570", "market": "KR"},
    {"name": "넷마블", "ticker": "251270", "market": "KR"},
    {"name": "코스모화학", "ticker": "005420", "market": "KR"},
    # 미국 대형주
    {"name": "Apple", "ticker": "AAPL", "market": "US"},
    {"name": "Microsoft", "ticker": "MSFT", "market": "US"},
    {"name": "NVIDIA", "ticker": "NVDA", "market": "US"},
    {"name": "Amazon", "ticker": "AMZN", "market": "US"},
    {"name": "Google", "ticker": "GOOGL", "market": "US"},
    {"name": "Meta", "ticker": "META", "market": "US"},
    {"name": "Tesla", "ticker": "TSLA", "market": "US"},
    {"name": "Berkshire Hathaway", "ticker": "BRK-B", "market": "US"},
    {"name": "JPMorgan", "ticker": "JPM", "market": "US"},
    {"name": "Visa", "ticker": "V", "market": "US"},
    {"name": "Johnson & Johnson", "ticker": "JNJ", "market": "US"},
    {"name": "Walmart", "ticker": "WMT", "market": "US"},
    {"name": "Exxon Mobil", "ticker": "XOM", "market": "US"},
    {"name": "UnitedHealth", "ticker": "UNH", "market": "US"},
    {"name": "Netflix", "ticker": "NFLX", "market": "US"},
    {"name": "AMD", "ticker": "AMD", "market": "US"},
    {"name": "Intel", "ticker": "INTC", "market": "US"},
    {"name": "Qualcomm", "ticker": "QCOM", "market": "US"},
    {"name": "Disney", "ticker": "DIS", "market": "US"},
    {"name": "Palantir", "ticker": "PLTR", "market": "US"},
]


def search_stocks(query: str) -> list[dict]:
    """이름 또는 티커로 검색. 최대 8개 반환. 목록에 없으면 입력값을 티커로 직접 반환."""
    q = query.strip()
    if not q:
        return []
    results = [
        s for s in STOCKS
        if q.lower() in s["name"].lower() or q.lower() in s["ticker"].lower()
    ]
    if results:
        return results[:8]
    # 목록에 없는 티커도 직접 추가할 수 있도록 그대로 반환
    return [{"name": q.upper(), "ticker": q.upper(), "market": "US"}]
