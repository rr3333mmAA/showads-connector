import re

from .config import Config
from .models import AgeLimit, Customer

_NAME_RE = re.compile(r"^[A-Za-z ]+$")

def validate_customer(customer: Customer, age_limit: AgeLimit, config: Config) -> bool:
    if not _NAME_RE.match(customer.name.strip()):
        return False
    if not age_limit.is_valid(customer.age):
        return False
    if not (config.min_banner_id <= customer.banner_id <= config.max_banner_id):
        return False
    return True
