import logging
import time
from dataclasses import dataclass
from typing import Iterable, Optional, cast

import requests

from .config import Config
from .models import Banner

logger = logging.getLogger(__name__)

@dataclass
class Token:
    access_token: str
    expires_at: float

    def is_valid(self) -> bool:
        return self.expires_at > time.time()

class ShowAdsClient:
    def __init__(self, config: Config):
        self._config = config
        self._token: Optional[Token] = None
        self._session = requests.Session()

    def _auth_header(self) -> dict[str, str]:
        token = self._token
        if token is None or not token.is_valid():
            token = self._refresh_token()
        return {"Authorization": f"Bearer {token.access_token}"}

    def _refresh_token(self) -> Token:
        url = f"{self._config.api_base_url}/auth"
        payload = {
            "ProjectKey": self._config.project_key
        }
        for attempt in range(self._config.max_retries):
            try:
                response = self._session.post(url, json=payload)
                if response.status_code == 200:
                    data = cast(dict[str, str], response.json())
                    access_token = data.get("AccessToken")
                    if not access_token:
                        raise RuntimeError("Missing AccessToken in auth response")
                    token = Token(
                        access_token=access_token,
                        expires_at=time.time() + self._config.token_expiry_seconds
                    )
                    self._token = token
                    logger.info("Obtained access token")
                    return token
                if response.status_code in (401, 400):
                    raise RuntimeError(f"Auth request failed: {response.status_code} {response.text}")
                # if status_code in (429, 500), we continue with backoff
                self._backoff(attempt)
            except requests.RequestException as e:
                logger.warning(f"Auth request error: {e}")
                self._backoff(attempt)
        raise RuntimeError("Failed to obtain access token")
    
    def _backoff(self, attempt: int) -> None:
        delay = self._config.retry_backoff_seconds * (2.0 ** attempt)
        time.sleep(min(delay, 30))

    def show_banner(self, banner: Banner) -> bool:
        url = f"{self._config.api_base_url}/banners/show"
        payload = {
            "VisitorCookie": banner.visitor_cookie,
            "BannerId": banner.banner_id
        }
        return self._post_with_retry(url, payload)
    
    def show_banners_bulk(self, banners: Iterable[Banner]) -> bool:
        url = f"{self._config.api_base_url}/banners/show/bulk"
        items = [{"VisitorCookie": banner.visitor_cookie, "BannerId": banner.banner_id} for banner in banners]
        payload = {"Data": items}
        return self._post_with_retry(url, payload)
    
    def _post_with_retry(self, url: str, payload: object) -> bool:
        for attempt in range(self._config.max_retries):
            try:
                headers = {"Content-Type": "application/json"}
                headers.update(self._auth_header())
                response = self._session.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    return True
                if response.status_code == 401:
                    logger.info("Access token expired or invalid, refreshing")
                    self._refresh_token()
                    continue
                if response.status_code == 400:
                    logger.error(f"Bad request {response.status_code}: {response.text}")
                    return False
                # if status_code in (429, 500), we continue with backoff
                self._backoff(attempt)
            except requests.RequestException as e:
                logger.warning(f"Request error: {e}")
        return False
