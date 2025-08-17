import logging
from pathlib import Path

from .config import Config
from .csv_loader import CsvSource
from .models import AgeLimit, Banner
from .showads_client import ShowAdsClient
from .validation import validate_customer

logger = logging.getLogger(__name__)

def process_csv(path: str, config: Config, age_limit: AgeLimit, client: ShowAdsClient) -> None:
    source = CsvSource(Path(path))

    buffer: list[Banner] = []
    valid_customers = 0
    invalid_customers = 0
    for customer in source.row():
        is_valid, error_message = validate_customer(customer, age_limit, config)
        if not is_valid:
            invalid_customers += 1
            logger.error(f"Invalid customer skipped: {error_message}")
            continue
        banner = Banner.from_customer(customer)
        buffer.append(banner)
        valid_customers += 1
        if len(buffer) >= config.bulk_batch_size:
            _show_banners_with_fallback(client, buffer)
            buffer.clear()
    
    # Show remaining banners
    if buffer:
        _show_banners_with_fallback(client, buffer)

    logger.info(f"Processed customers: {valid_customers} valid, {invalid_customers} invalid")

def _show_banners_with_fallback(client: ShowAdsClient, banners: list[Banner]) -> None:
    """Show banners in bulk, falling back to single banner requests if bulk fails."""
    if client.show_banners_bulk(banners):
        return
    logger.error("Failed to show banners in bulk, falling back to single banner requests")

    for banner in banners:
        if not client.show_banner(banner):
            logger.error(f"Failed to show banner: {banner}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = Config.load()
    age_limit = AgeLimit()
    client = ShowAdsClient(config)
    print("Processing data_valid.csv")
    process_csv("data_valid.csv", config, age_limit, client)
    print("Processing data_invalid.csv")
    process_csv("data_invalid.csv", config, age_limit, client)