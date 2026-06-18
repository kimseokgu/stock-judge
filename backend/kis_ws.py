import os
import json
import httpx
import websockets
from kis_auth import APP_KEY, APP_SECRET
from kis_client import is_korean, _get_exchange_code

KIS_WS_URL = "wss://ops.koreainvestment.com:21000"


async def stream_price(ticker: str, client_ws):
    """KIS WebSocket에서 실시간 시세 수신 후 client_ws로 중계."""
    try:
        approval_key = _get_approval_key()
        async with websockets.connect(KIS_WS_URL, open_timeout=10) as kis_ws:
            sub_msg = _build_subscribe_msg(ticker, approval_key)
            await kis_ws.send(json.dumps(sub_msg))

            async for raw in kis_ws:
                if isinstance(raw, str) and (raw.startswith("0|") or raw.startswith("1|")):
                    price_data = _parse_price(raw, ticker)
                    if price_data:
                        await client_ws.send_text(json.dumps(price_data))
    except Exception:
        # KIS WebSocket 접속 실패 시 (해외 서버 등) 조용히 종료
        pass


def _build_subscribe_msg(ticker: str, approval_key: str) -> dict:
    if is_korean(ticker):
        tr_id = "H0STCNT0"
        tr_key = ticker.replace(".KS", "").replace(".KQ", "")
    else:
        tr_id = "HDFSCNT0"
        tr_key = f"{_get_exchange_code(ticker)}|{ticker}"

    return {
        "header": {
            "approval_key": approval_key,
            "custtype": "P",
            "tr_type": "1",
            "content-type": "utf-8",
        },
        "body": {
            "input": {"tr_id": tr_id, "tr_key": tr_key}
        },
    }


def _get_approval_key() -> str:
    base_url = os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")
    resp = httpx.post(
        f"{base_url}/oauth2/Approval",
        json={"grant_type": "client_credentials", "appkey": APP_KEY, "secretkey": APP_SECRET},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["approval_key"]


def _parse_price(raw: str, ticker: str) -> dict | None:
    parts = raw.split("|")
    if len(parts) < 4:
        return None
    data = parts[3].split("^")
    try:
        if is_korean(ticker):
            return {"price": float(data[2]), "volume": int(data[12])}
        else:
            return {"price": float(data[11]), "volume": int(data[12])}
    except (IndexError, ValueError):
        return None
