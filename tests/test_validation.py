from src.config import Config
from src.models import AgeLimit, Customer
from src.validation import validate_customer


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


def test_validate_customer_happy_path():
    config = make_config(min_banner_id=1, max_banner_id=10)
    age_limit = AgeLimit(min_age=18, max_age=65)
    customer = Customer(name="John Doe", age=30, cookie="c1", banner_id=5)

    is_valid, error = validate_customer(customer, age_limit, config)

    assert is_valid is True
    assert error is None


def test_validate_customer_name_must_be_letters_and_spaces():
    config = make_config()
    age_limit = AgeLimit()
    customer = Customer(name="John3", age=30, cookie="c1", banner_id=5)

    is_valid, error = validate_customer(customer, age_limit, config)

    assert is_valid is False
    assert "invalid name" in error


def test_validate_customer_age_below_min_is_invalid():
    config = make_config()
    age_limit = AgeLimit(min_age=21, max_age=65)
    customer = Customer(name="John", age=20, cookie="c3", banner_id=10)

    is_valid, error = validate_customer(customer, age_limit, config)

    assert is_valid is False
    assert f"between {age_limit.min_age} and {age_limit.max_age}" in error


def test_validate_customer_age_above_max_is_invalid():
    config = make_config()
    age_limit = AgeLimit(min_age=18, max_age=30)
    customer = Customer(name="John", age=31, cookie="c4", banner_id=10)

    is_valid, error = validate_customer(customer, age_limit, config)

    assert is_valid is False
    assert f"between {age_limit.min_age} and {age_limit.max_age}" in error


def test_validate_customer_age_on_boundaries_is_valid():
    config = make_config()
    age_limit = AgeLimit(min_age=18, max_age=30)

    low = Customer(name="John", age=18, cookie="c5", banner_id=10)
    high = Customer(name="John", age=30, cookie="c5", banner_id=10)

    is_valid_low, _ = validate_customer(low, age_limit, config)
    is_valid_high, _ = validate_customer(high, age_limit, config)

    assert is_valid_low is True
    assert is_valid_high is True


def test_validate_customer_banner_id_below_min_is_invalid():
    config = make_config(min_banner_id=10, max_banner_id=20)
    age_limit = AgeLimit()
    customer = Customer(name="John", age=28, cookie="c6", banner_id=9)

    is_valid, error = validate_customer(customer, age_limit, config)

    assert is_valid is False
    assert f"between {config.min_banner_id} and {config.max_banner_id}" in error


def test_validate_customer_banner_id_above_max_is_invalid():
    config = make_config(min_banner_id=10, max_banner_id=20)
    age_limit = AgeLimit()
    customer = Customer(name="John", age=28, cookie="c7", banner_id=21)

    is_valid, error = validate_customer(customer, age_limit, config)

    assert is_valid is False
    assert f"between {config.min_banner_id} and {config.max_banner_id}" in error
