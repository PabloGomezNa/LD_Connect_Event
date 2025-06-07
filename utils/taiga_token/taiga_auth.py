import os, requests, logging, time
from config.settings import TAIGA_USERNAME, TAIGA_PASSWORD

log = logging.getLogger(__name__)
_TOKEN      = None
_EXPIRES_AT = 0          # timestamp in seconds

def get_taiga_token() -> str:
    '''
    Tool to get a Taiga API token and cache it for 23 hours (In taiga documentation, says the token expires in 24h).
    If the token is about to expire (less than 60 seconds left), it will request a new one.
    This avoids making too many requests to the Taiga API for the token.
    '''
    global _TOKEN, _EXPIRES_AT
    # If the token is not set or is about to expire, request a new one
    if not _TOKEN or _EXPIRES_AT - time.time() < 60:
        url = "https://api.taiga.io/api/v1/auth"
        payload = {
            "username": TAIGA_USERNAME,
            "password": TAIGA_PASSWORD,
            "type": "normal",
        }
        r = requests.post(url, json=payload, timeout=(2, 5))
        r.raise_for_status()
        js = r.json()
        _TOKEN       = js["auth_token"]
        _EXPIRES_AT  = time.time() + 23*3600         # 23 hours from now
        log.info("New Taiga token acquired successfully, expires in 23h.")
    return _TOKEN
