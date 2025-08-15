from typing import cast

import requests

from .config import Config

config: Config = Config.load()
session: requests.Session = requests.Session()

def auth() -> dict[str, str]:
    payload = {
        "ProjectKey": config.project_key
    }
    response = session.post(f"{config.api_base_url}/auth", json=payload)
    response.raise_for_status()
    return cast(dict[str, str], response.json())

print(auth())




