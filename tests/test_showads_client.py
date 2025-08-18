import pytest

from src.config import Config
from src.models import Banner
from src.showads_client import ShowAdsClient

def make_config(**overrides) -> Config:
    base = dict(
        api_base_url="https://api.example",
        project_key="dev-key",
        min_banner_id=1,
        max_banner_id=99,
        token_expiry_seconds=84600,
        max_retries=5,
        retry_backoff_seconds=2,
        bulk_batch_size=1000,
    )
    base.update(overrides)
    return Config(**base)

def test_auth_success_returns_bearer_header(requests_mock):
    config = make_config()
    client = ShowAdsClient(config)
    auth_url = f"{config.api_base_url}/auth"
    requests_mock.post(auth_url, json={"AccessToken": "abc"}, status_code=200)

    header = client._auth_header()

    assert header["Authorization"] == "Bearer abc"
    first = requests_mock.request_history[0]
    assert first.url == auth_url
    assert first.json() == {"ProjectKey": config.project_key}


def test_auth_retries_on_500_then_succeeds(requests_mock):
    config = make_config(max_retries=5)
    client = ShowAdsClient(config)
    auth_url = f"{config.api_base_url}/auth"
    requests_mock.post(auth_url, [
        {"status_code": 500},
        {"status_code": 500},
        {"json": {"AccessToken": "abc"}, "status_code": 200},
    ])

    header = client._auth_header()

    assert header["Authorization"] == "Bearer abc"
    # 3 attempts: two 500s then a 200
    assert len(requests_mock.request_history) == 3


def test_auth_400_raises_runtime_error(requests_mock):
    config = make_config()
    client = ShowAdsClient(config)
    auth_url = f"{config.api_base_url}/auth"
    requests_mock.post(auth_url, status_code=400, text="bad request")

    with pytest.raises(RuntimeError):
        client._auth_header()


def test_show_banner_success_builds_correct_request_and_headers(requests_mock):
    config = make_config()
    client = ShowAdsClient(config)
    auth_url = f"{config.api_base_url}/auth"
    show_url = f"{config.api_base_url}/banners/show"
    requests_mock.post(auth_url, json={"AccessToken": "abc"})
    requests_mock.post(show_url, status_code=200)

    ok = client.show_banner(Banner(visitor_cookie="cookie-1", banner_id=7))

    assert ok is True
    last_call = requests_mock.request_history[-1]
    assert last_call.url == show_url
    assert last_call.json() == {"VisitorCookie": "cookie-1", "BannerId": 7}
    assert last_call.headers["Content-Type"] == "application/json"
    assert last_call.headers["Authorization"] == "Bearer abc"


def test_show_banners_bulk_success_payload_shape(requests_mock):
    config = make_config()
    client = ShowAdsClient(config)
    auth_url = f"{config.api_base_url}/auth"
    bulk_url = f"{config.api_base_url}/banners/show/bulk"
    requests_mock.post(auth_url, json={"AccessToken": "abc"})
    requests_mock.post(bulk_url, status_code=200)

    banners = [
        Banner(visitor_cookie="c1", banner_id=1),
        Banner(visitor_cookie="c2", banner_id=2),
    ]
    ok = client.show_banners_bulk(banners)

    assert ok is True
    last_call = requests_mock.request_history[-1]
    assert last_call.url == bulk_url
    assert last_call.json() == {
        "Data": [
            {"VisitorCookie": "c1", "BannerId": 1},
            {"VisitorCookie": "c2", "BannerId": 2},
        ]
    }
    assert last_call.headers["Authorization"] == "Bearer abc"
