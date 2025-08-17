import logging
from pathlib import Path

from .config import Config
from .csv_loader import CsvSource
from .models import AgeLimit, Banner
from .showads_client import ShowAdsClient
from .validation import validate_customer

logger = logging.getLogger(__name__)

def process_csv(path: str, config: Config, age_limit: AgeLimit) -> None:
    source = CsvSource(Path(path))
    client = ShowAdsClient(config)

    valid_customers = 0
    invalid_customers = 0
    for customer in source.row():
        if not validate_customer(customer, age_limit, config):
            invalid_customers += 1
            continue
        banner = Banner.from_customer(customer)
        client.show_banner(banner)
        valid_customers += 1

    logger.info(f"Processed customers: {valid_customers} valid, {invalid_customers} invalid")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = Config.load()
    age_limit = AgeLimit()
    print("Processing data_valid.csv")
    process_csv("data_valid.csv", config, age_limit)
    print("Processing data_invalid.csv")
    process_csv("data_invalid.csv", config, age_limit)