import logging
import os


def setup_logging() -> None:
	"""Configure root logger from LOG_LEVEL env var (defaults to INFO)."""
	level_name: str = os.getenv("LOG_LEVEL", "INFO").upper()
	level_value: int = getattr(logging, level_name, logging.INFO)
	logging.basicConfig(
		level=level_value
	)