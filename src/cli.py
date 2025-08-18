import argparse
import logging
import os
import sys
from typing import cast

from .config import Config
from .models import AgeLimit
from .processor import process_csv
from .showads_client import ShowAdsClient


def _setup_logging() -> None:
	"""Configure root logger from LOG_LEVEL env var (defaults to INFO)."""
	level_name: str = os.getenv("LOG_LEVEL", "INFO").upper()
	level_value: int = getattr(logging, level_name, logging.INFO)
	logging.basicConfig(
		level=level_value
	)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
	"""Parse command-line arguments.

	Returns parsed arguments namespace.
	"""
	parser = argparse.ArgumentParser(description="Send CSV customers to ShowAds")
	parser.add_argument(
		"csv_path",
		type=str,
		help="Path to CSV file with customers data",
	)
	parser.add_argument(
		"--age-limit",
		type=int,
		nargs=2,
		metavar=("MIN", "MAX"),
		help="Age limit for customers as two integers: MIN MAX",
	)
	return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
	"""CLI entrypoint.

	Returns a POSIX-style exit code where 0 indicates success.
	"""
	_setup_logging()
	args = _parse_args(argv)

	config = Config.load()
	if args.age_limit is None:  # type: ignore
		age_limit = AgeLimit()
	else:
		min_age, max_age = cast(tuple[int, int], args.age_limit)
		age_limit = AgeLimit(min_age=min_age, max_age=max_age)

	client = ShowAdsClient(config)
	csv_path: str = args.csv_path
	process_csv(
		path=csv_path,
		config=config,
		age_limit=age_limit,
		client=client,
	)
	return 0


if __name__ == "__main__":
	sys.exit(main())
