import logging
import time
from dataclasses import dataclass
from typing import Optional, cast

import requests

from .config import Config

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
        response = self._session.post(url, json=payload)
        response.raise_for_status()
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

if __name__ == "__main__":
    config = Config.load()
    client = ShowAdsClient(config)
    print(client._auth_header())