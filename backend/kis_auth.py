import os
import time
import json
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")
BASE_URL = os.getenv("KIS_BASE_URL", "https://openapi.koreainvestment.com:9443")

_CACHE_FILE = Path(__file__).parent / ".token_cache.json"


def get_token() -> str:
    # 파일 캐시에서 유효한 토큰이 있으면 재사용
    if _CACHE_FILE.exists():
        try:
            cached = json.loads(_CACHE_FILE.read_text())
            if time.time() < cached["expires_at"] - 60:
                return cached["access_token"]
        except (KeyError, ValueError):
            pass

    token, expires_at = _issue_token()
    _CACHE_FILE.write_text(json.dumps({"access_token": token, "expires_at": expires_at}))
    return token


def _issue_token() -> tuple[str, float]:
    url = f"{BASE_URL}/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }
    resp = httpx.post(url, json=body, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    expires_at = time.time() + int(data["expires_in"])
    return data["access_token"], expires_at


def auth_headers() -> dict:
    return {
        "authorization": f"Bearer {get_token()}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "content-type": "application/json; charset=utf-8",
    }
