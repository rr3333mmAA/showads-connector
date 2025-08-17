import re
from typing import Tuple

from .config import Config
from .models import AgeLimit, Customer

_NAME_RE = re.compile(r"^[A-Za-z ]+$")

def validate_customer(customer: Customer, age_limit: AgeLimit, config: Config) -> Tuple[bool, str | None]:
    """Validate a customer record.

    Returns (is_valid, error_message). Error is None when valid.
    """

    if not _NAME_RE.match(customer.name.strip()):
        return False, f"invalid name: must contain only letters and spaces (got {customer.name})"
    if not age_limit.is_valid(customer.age):
        return False, f"invalid age: must be between {age_limit.min_age} and {age_limit.max_age} (got {customer.age})"
    if not (config.min_banner_id <= customer.banner_id <= config.max_banner_id):
        return False, f"invalid banner id: must be between {config.min_banner_id} and {config.max_banner_id} (got {customer.banner_id})"
    return True, None
