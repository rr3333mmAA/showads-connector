from src.config import Config
from src.models import AgeLimit
import src.cli as cli


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

def test_main_happy_path_default_age(monkeypatch):
    config = make_config()

    # Stub Config.load
    monkeypatch.setattr(cli.Config, "load", lambda: config)

    # Capture constructed client and process_csv call
    constructed = {}

    class DummyClient:
        def __init__(self, cfg: Config):
            constructed["config"] = cfg

    monkeypatch.setattr(cli, "ShowAdsClient", DummyClient)

    called = {}

    def fake_process_csv(path, config, age_limit, client):
        called["args"] = dict(path=path, config=config, age_limit=age_limit, client=client)

    monkeypatch.setattr(cli, "process_csv", fake_process_csv)

    rc = cli.main(["data.csv"])

    assert rc == 0
    assert constructed["config"] == config
    assert called["args"]["path"] == "data.csv"
    assert called["args"]["config"] == config
    assert called["args"]["age_limit"] == AgeLimit()
    assert isinstance(called["args"]["client"], DummyClient)


def test_main_with_age_limit(monkeypatch):
    config = make_config()
    monkeypatch.setattr(cli.Config, "load", lambda: config)

    captured = {}

    def fake_process_csv(path, config, age_limit, client):
        captured["age_limit"] = age_limit
        captured["path"] = path

    monkeypatch.setattr(cli, "process_csv", fake_process_csv)

    rc = cli.main(["data.csv", "--age-limit", "21", "65"])

    assert rc == 0
    assert captured["path"] == "data.csv"
    assert captured["age_limit"] == AgeLimit(min_age=21, max_age=65)
